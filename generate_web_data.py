from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tabelas"
WEB_DATA = ROOT / "web" / "data"
WEB_JS = ROOT / "web" / "js"

ID_ROSARIO = "2806107"
DRE4_IDS = {
    "2801306": "Capela",
    "2801504": "Carmopolis",
    "2802007": "Divina Pastora",
    "2802502": "General Maynard",
    "2803302": "Japaratuba",
    "2805307": "Pirambu",
    "2806107": "Rosario do Catete",
    "2806503": "Santa Rosa de Lima",
    "2807204": "Siriri",
}
STAGES = {
    "iniciais (1-5)": "Anos Iniciais",
    "finais (6-9)": "Anos Finais",
}


def clean(value):
    if pd.isna(value):
        return None
    if isinstance(value, float):
        return round(value, 6)
    if hasattr(value, "item"):
        return clean(value.item())
    return value


def records(df: pd.DataFrame):
    return [{k: clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def rank_seq(df: pd.DataFrame, groups: list[str], label_col: str) -> pd.DataFrame:
    out = df[df["ideb"].notna()].copy()
    out = out.sort_values(groups + ["ideb", label_col], ascending=[True] * len(groups) + [False, True])
    out["posicao"] = out.groupby(groups).cumcount() + 1
    return out


def stage_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["etapa"] = out["anos_escolares"].map(STAGES)
    return out


def validate(data: dict) -> list[str]:
    warnings = []
    municipio = data["municipio"]
    if len(municipio) != 2:
        raise ValueError("Comparativo municipal deve conter duas etapas.")
    for row in municipio:
        for key in ["ideb_2023", "ideb_2025", "variacao_absoluta", "variacao_percentual"]:
            if row.get(key) is None:
                raise ValueError(f"Indicador ausente em municipio: {key}")
    if not data["escolas"]:
        raise ValueError("Nenhuma escola comparavel encontrada.")
    for stage in ["Anos Iniciais", "Anos Finais"]:
        for year in [2023, 2025]:
            subset = [r for r in data["dre4"] if r["etapa"] == stage and r["ano"] == year]
            present = {r["municipio_dre4"] for r in subset}
            missing = set(DRE4_IDS.values()) - present
            if missing:
                warnings.append(f"DRE 4 {year} {stage}: sem IDEB disponivel para {sorted(missing)}")
    return warnings


def main() -> None:
    rosario = stage_label(pd.read_csv(TABLES / "comparativo_rosario.csv", dtype={"id_municipio": str}))
    rosario = rosario.drop(columns=[c for c in rosario.columns if c.startswith("posicao_dre4_") or c == "mudanca_posicao_dre4"], errors="ignore")
    escolas = stage_label(pd.read_csv(TABLES / "comparativo_escolas.csv", dtype={"id_municipio": str, "id_escola": str}))
    ranking_dre4 = stage_label(pd.read_csv(TABLES / "ranking_dre4.csv", dtype={"id_municipio": str}))
    dre4_variacao = stage_label(pd.read_csv(TABLES / "dre4_variacao.csv", dtype={"id_municipio": str}))
    ranking_estadual = stage_label(pd.read_csv(TABLES / "ranking_estadual.csv", dtype={"id_municipio": str}))

    dre4_ranked = rank_seq(ranking_dre4, ["ano", "anos_escolares"], "municipio_dre4")
    dre4_ranked = dre4_ranked[[
        "ano", "id_municipio", "municipio", "municipio_dre4", "anos_escolares", "etapa",
        "ideb", "indicador_rendimento", "nota_saeb_media_padronizada", "posicao"
    ]]

    sergipe = ranking_estadual.groupby(["ano", "anos_escolares", "etapa"], as_index=False).agg(
        ideb=("ideb", "mean"),
        indicador_rendimento=("indicador_rendimento", "mean"),
        nota_saeb_media_padronizada=("nota_saeb_media_padronizada", "mean"),
        municipios_com_ideb=("id_municipio", "nunique"),
    )

    dre4_media = ranking_dre4.groupby(["ano", "anos_escolares", "etapa"], as_index=False).agg(
        ideb=("ideb", "mean"),
        municipios_com_ideb=("id_municipio", "nunique"),
    )

    dre4_pos = dre4_ranked[dre4_ranked["id_municipio"] == ID_ROSARIO][["ano", "anos_escolares", "posicao"]]
    for year in [2023, 2025]:
        rosario = rosario.merge(
            dre4_pos[dre4_pos["ano"] == year].drop(columns="ano").rename(columns={"posicao": f"posicao_dre4_{year}"}),
            on="anos_escolares",
            how="left",
        )
    rosario["mudanca_posicao_dre4"] = rosario["posicao_dre4_2023"] - rosario["posicao_dre4_2025"]

    gaps = []
    for _, row in rosario.iterrows():
        for year in [2023, 2025]:
            ser = sergipe[(sergipe["ano"] == year) & (sergipe["anos_escolares"] == row["anos_escolares"])]
            dre = dre4_media[(dre4_media["ano"] == year) & (dre4_media["anos_escolares"] == row["anos_escolares"])]
            gaps.append({
                "ano": year,
                "anos_escolares": row["anos_escolares"],
                "etapa": row["etapa"],
                "rosario_ideb": row[f"ideb_{year}"],
                "sergipe_media_municipal": ser["ideb"].iloc[0] if not ser.empty else None,
                "dre4_media": dre["ideb"].iloc[0] if not dre.empty else None,
                "gap_sergipe": row[f"ideb_{year}"] - (ser["ideb"].iloc[0] if not ser.empty else float("nan")),
                "gap_dre4": row[f"ideb_{year}"] - (dre["ideb"].iloc[0] if not dre.empty else float("nan")),
            })

    escolas_validas = escolas[escolas["ideb_2023"].notna() & escolas["ideb_2025"].notna()].copy()
    escolas_validas["status"] = "Estaveis"
    escolas_validas.loc[escolas_validas["variacao_absoluta"] > 0, "status"] = "Avancaram"
    escolas_validas.loc[escolas_validas["variacao_absoluta"] < 0, "status"] = "Recuaram"

    indicadores = {
        "total_escolas_comparaveis": int(len(escolas_validas)),
        "escolas_avancaram": int((escolas_validas["variacao_absoluta"] > 0).sum()),
        "escolas_estaveis": int((escolas_validas["variacao_absoluta"] == 0).sum()),
        "escolas_recuaram": int((escolas_validas["variacao_absoluta"] < 0).sum()),
        "maior_avanco_escola": clean(escolas_validas.sort_values("variacao_absoluta", ascending=False).iloc[0].to_dict()),
        "menor_ideb_2025_etapa": clean(rosario.sort_values("ideb_2025").iloc[0].to_dict()),
    }

    data = {
        "meta": {
            "municipio": "Rosario do Catete",
            "uf": "SE",
            "rede": "municipal",
            "anos": [2023, 2025],
            "fonte": "INEP / Base dos Dados / analise propria",
            "observacao_sergipe": "Sergipe e representado pela media municipal dos municipios sergipanos com IDEB disponivel.",
        },
        "municipio": records(rosario),
        "sergipe": records(sergipe),
        "gaps": records(pd.DataFrame(gaps)),
        "dre4": records(dre4_ranked),
        "dre4_variacao": records(dre4_variacao),
        "escolas": records(escolas_validas),
        "indicadores": indicadores,
    }

    warnings = validate(data)
    data["validacao"] = {"warnings": warnings}

    WEB_DATA.mkdir(parents=True, exist_ok=True)
    WEB_JS.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(data, ensure_ascii=False, indent=2)
    (WEB_DATA / "ideb_data.json").write_text(json_text, encoding="utf-8")
    (WEB_JS / "data.js").write_text("window.IDEB_DATA = " + json_text + ";\n", encoding="utf-8")
    print("JSON gerado:", WEB_DATA / "ideb_data.json")
    for warning in warnings:
        print("Aviso:", warning)


if __name__ == "__main__":
    main()
