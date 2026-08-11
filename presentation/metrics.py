from __future__ import annotations

import math
import pandas as pd

from .config import ID_MUNICIPIO_ROSARIO, PRESENTATION_TABLES_DIR

ETAPA_LABEL = {
    "iniciais (1-5)": "Anos iniciais",
    "finais (6-9)": "Anos finais",
}


def fmt_num(value: float | int | None, digits: int = 1, signed: bool = False) -> str:
    if value is None or pd.isna(value):
        return "-"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:.{digits}f}".replace(".", ",")


def fmt_pct(value: float | int | None, digits: int = 1, signed: bool = True) -> str:
    if value is None or pd.isna(value):
        return "-"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:.{digits}f}%".replace(".", ",")


def fmt_rank(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{int(value)}º"


def sequential_rank(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    ranked = df[df["ideb"].notna()].copy()
    ranked = ranked.sort_values(group_cols + ["ideb", "municipio"], ascending=[True] * len(group_cols) + [False, True])
    ranked["ranking_seq"] = ranked.groupby(group_cols).cumcount() + 1
    return ranked


def add_stage(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["etapa"] = out["anos_escolares"].map(ETAPA_LABEL).fillna(out["anos_escolares"])
    return out


def build_metrics(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame | dict]:
    rosario = add_stage(data["rosario"])
    escolas = add_stage(data["escolas"])
    ranking_estadual = add_stage(data["ranking_estadual"])
    ranking_dre4 = add_stage(data["ranking_dre4"])
    dre4_variacao = add_stage(data["dre4_variacao"])

    ranking_estadual_seq = sequential_rank(ranking_estadual, ["ano", "anos_escolares"])
    ranking_dre4_seq = sequential_rank(ranking_dre4, ["ano", "anos_escolares"])

    seq_rosario = ranking_estadual_seq[ranking_estadual_seq["id_municipio"] == ID_MUNICIPIO_ROSARIO][["ano", "anos_escolares", "ranking_seq"]]
    seq_dre4_rosario = ranking_dre4_seq[ranking_dre4_seq["id_municipio"] == ID_MUNICIPIO_ROSARIO][["ano", "anos_escolares", "ranking_seq"]]
    for ano in [2023, 2025]:
        rosario = rosario.merge(
            seq_rosario[seq_rosario["ano"] == ano].drop(columns="ano").rename(columns={"ranking_seq": f"ranking_estadual_seq_{ano}"}),
            on="anos_escolares",
            how="left",
        )
        rosario = rosario.merge(
            seq_dre4_rosario[seq_dre4_rosario["ano"] == ano].drop(columns="ano").rename(columns={"ranking_seq": f"ranking_dre4_seq_{ano}"}),
            on="anos_escolares",
            how="left",
        )
    rosario["mudanca_ranking_estadual_seq"] = rosario["ranking_estadual_seq_2023"] - rosario["ranking_estadual_seq_2025"]
    rosario["mudanca_ranking_dre4_seq"] = rosario["ranking_dre4_seq_2023"] - rosario["ranking_dre4_seq_2025"]

    media_sergipe = ranking_estadual.groupby(["ano", "anos_escolares", "etapa"], as_index=False).agg(
        ideb=("ideb", "mean"),
        indicador_rendimento=("indicador_rendimento", "mean"),
        nota_saeb_media_padronizada=("nota_saeb_media_padronizada", "mean"),
    )
    media_dre4 = ranking_dre4.groupby(["ano", "anos_escolares", "etapa"], as_index=False).agg(
        ideb=("ideb", "mean"),
        indicador_rendimento=("indicador_rendimento", "mean"),
        nota_saeb_media_padronizada=("nota_saeb_media_padronizada", "mean"),
    )

    resumo = rosario[["anos_escolares", "etapa", "ideb_2023", "ideb_2025", "variacao_absoluta", "variacao_percentual", "ranking_estadual_seq_2025", "ranking_dre4_seq_2025"]].copy()
    resumo = resumo.rename(columns={"ranking_estadual_seq_2025": "posicao_estadual_2025", "ranking_dre4_seq_2025": "posicao_dre4_2025"})

    escolas_validas = escolas[escolas["ideb_2023"].notna() & escolas["ideb_2025"].notna()].copy()
    contagem_escolas = {
        "avancaram": int((escolas_validas["variacao_absoluta"] > 0).sum()),
        "estaveis": int((escolas_validas["variacao_absoluta"] == 0).sum()),
        "recuaram": int((escolas_validas["variacao_absoluta"] < 0).sum()),
        "comparaveis": int(len(escolas_validas)),
    }
    maior_avanco_escola = escolas_validas.sort_values("variacao_absoluta", ascending=False).head(1)
    maior_queda_escola = escolas_validas.sort_values("variacao_absoluta", ascending=True).head(1)

    dre4_validas = dre4_variacao[dre4_variacao["ideb_2023"].notna() & dre4_variacao["ideb_2025"].notna()].copy()
    maior_avanco_dre4 = dre4_validas.sort_values("variacao_absoluta", ascending=False).head(1)
    maior_queda_dre4 = dre4_validas.sort_values("variacao_absoluta", ascending=True).head(1)

    PRESENTATION_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    resumo.to_csv(PRESENTATION_TABLES_DIR / "resumo_executivo.csv", index=False, encoding="utf-8-sig")
    ranking_dre4_seq[ranking_dre4_seq["ano"] == 2025].to_csv(PRESENTATION_TABLES_DIR / "ranking_dre4_2025.csv", index=False, encoding="utf-8-sig")
    ranking_estadual_seq[ranking_estadual_seq["ano"] == 2025].to_csv(PRESENTATION_TABLES_DIR / "ranking_estadual_2025.csv", index=False, encoding="utf-8-sig")
    escolas_validas.sort_values("variacao_absoluta", ascending=False).to_csv(PRESENTATION_TABLES_DIR / "variacao_escolas.csv", index=False, encoding="utf-8-sig")
    rosario.to_csv(PRESENTATION_TABLES_DIR / "indicadores_municipio.csv", index=False, encoding="utf-8-sig")

    return {
        "rosario": rosario,
        "escolas": escolas,
        "escolas_validas": escolas_validas,
        "ranking_estadual": ranking_estadual,
        "ranking_estadual_seq": ranking_estadual_seq,
        "ranking_dre4": ranking_dre4,
        "ranking_dre4_seq": ranking_dre4_seq,
        "dre4_variacao": dre4_variacao,
        "media_sergipe": media_sergipe,
        "media_dre4": media_dre4,
        "resumo": resumo,
        "contagem_escolas": contagem_escolas,
        "maior_avanco_escola": maior_avanco_escola,
        "maior_queda_escola": maior_queda_escola,
        "maior_avanco_dre4": maior_avanco_dre4,
        "maior_queda_dre4": maior_queda_dre4,
    }
