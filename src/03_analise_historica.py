from __future__ import annotations

from pathlib import Path

import pandas as pd
from google.cloud import bigquery


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABELAS_DIR = PROJECT_ROOT / "outputs" / "tabelas"
BILLING_PROJECT = "cosmic-attic-499623-i4"
ID_MUNICIPIO_ROSARIO = "2806107"
IDS_MUNICIPIOS_DRE4 = {
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
INDICADORES = [
    "taxa_aprovacao",
    "indicador_rendimento",
    "nota_saeb_matematica",
    "nota_saeb_lingua_portuguesa",
    "nota_saeb_media_padronizada",
    "ideb",
]


QUERY_MUNICIPIOS_2023 = """
SELECT
    i.ano,
    i.sigla_uf,
    i.id_municipio,
    m.nome AS municipio,
    i.rede,
    i.ensino,
    i.anos_escolares,
    i.taxa_aprovacao,
    i.indicador_rendimento,
    i.nota_saeb_matematica,
    i.nota_saeb_lingua_portuguesa,
    i.nota_saeb_media_padronizada,
    i.ideb,
    i.projecao
FROM
    `basedosdados.br_inep_ideb.municipio` AS i
JOIN
    `basedosdados.br_bd_diretorios_brasil.municipio` AS m
    USING (id_municipio)
WHERE
    i.ano = 2023
    AND i.sigla_uf = 'SE'
    AND i.rede = 'municipal'
    AND i.ensino = 'fundamental'
    AND i.anos_escolares IN ('iniciais (1-5)', 'finais (6-9)')
"""

QUERY_ESCOLAS_2023 = """
SELECT
    i.ano,
    i.sigla_uf,
    i.id_municipio,
    i.id_escola,
    e.nome AS escola,
    i.rede,
    i.ensino,
    i.anos_escolares,
    i.taxa_aprovacao,
    i.indicador_rendimento,
    i.nota_saeb_matematica,
    i.nota_saeb_lingua_portuguesa,
    i.nota_saeb_media_padronizada,
    i.ideb,
    i.projecao
FROM
    `basedosdados.br_inep_ideb.escola` AS i
JOIN
    `basedosdados.br_bd_diretorios_brasil.escola` AS e
    USING (id_escola)
WHERE
    i.ano = 2023
    AND i.id_municipio = '2806107'
    AND i.rede = 'municipal'
    AND i.ensino = 'fundamental'
    AND i.anos_escolares IN ('iniciais (1-5)', 'finais (6-9)')
"""

QUERY_SERGIPE_2023 = """
SELECT
    ano,
    'SE' AS sigla_uf,
    'Sergipe' AS referencia,
    rede,
    ensino,
    anos_escolares,
    taxa_aprovacao,
    indicador_rendimento,
    nota_saeb_matematica,
    nota_saeb_lingua_portuguesa,
    nota_saeb_media_padronizada,
    ideb,
    projecao
FROM
    `basedosdados.br_inep_ideb.uf`
WHERE
    ano = 2023
    AND sigla_uf = 'SE'
    AND rede = 'municipal'
    AND ensino = 'fundamental'
    AND anos_escolares IN ('iniciais (1-5)', 'finais (6-9)')
"""


def consultar_bigquery(query: str) -> pd.DataFrame:
    client = bigquery.Client(project=BILLING_PROJECT)
    return client.query(query).result().to_dataframe()


def calcular_variacoes(df: pd.DataFrame, grupo: list[str]) -> pd.DataFrame:
    colunas_valores = INDICADORES + ["projecao"]
    partes = []
    for ano in [2023, 2025]:
        parte = df[df["ano"] == ano][grupo + colunas_valores].copy()
        parte = parte.rename(columns={col: f"{col}_{ano}" for col in colunas_valores})
        partes.append(parte)

    resultado = partes[0].merge(partes[1], on=grupo, how="outer")
    resultado["variacao_absoluta"] = resultado["ideb_2025"] - resultado["ideb_2023"]
    resultado["variacao_percentual"] = (
        resultado["variacao_absoluta"] / resultado["ideb_2023"] * 100
    )
    resultado["variacao_rendimento"] = (
        resultado["indicador_rendimento_2025"] - resultado["indicador_rendimento_2023"]
    )
    resultado["variacao_desempenho"] = (
        resultado["nota_saeb_media_padronizada_2025"]
        - resultado["nota_saeb_media_padronizada_2023"]
    )
    return resultado


def adicionar_rankings(municipios: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranking_estadual = municipios[municipios["ideb"].notna()].copy()
    ranking_estadual["posicao_estadual"] = (
        ranking_estadual.groupby(["ano", "anos_escolares"])["ideb"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    ranking_dre4 = ranking_estadual[
        ranking_estadual["id_municipio"].isin(IDS_MUNICIPIOS_DRE4)
    ].copy()
    ranking_dre4["municipio_dre4"] = ranking_dre4["id_municipio"].map(IDS_MUNICIPIOS_DRE4)
    ranking_dre4["posicao_dre4"] = (
        ranking_dre4.groupby(["ano", "anos_escolares"])["ideb"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    return ranking_estadual, ranking_dre4


def salvar_excel(abas: dict[str, pd.DataFrame], caminho: Path) -> None:
    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        for nome, df in abas.items():
            df.to_excel(writer, sheet_name=nome[:31], index=False)


def main() -> None:
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)

    municipios_2023 = consultar_bigquery(QUERY_MUNICIPIOS_2023)
    escolas_2023 = consultar_bigquery(QUERY_ESCOLAS_2023)
    sergipe_2023 = consultar_bigquery(QUERY_SERGIPE_2023)

    municipios_2025 = pd.read_csv(PROCESSED_DIR / "ideb_2025_municipios.csv", dtype={"id_municipio": str})
    escolas_2025 = pd.read_csv(PROCESSED_DIR / "ideb_2025_escolas.csv", dtype={"id_municipio": str, "id_escola": str})

    municipios_2025 = municipios_2025[
        (municipios_2025["sigla_uf"] == "SE")
        & (municipios_2025["rede"] == "municipal")
    ]
    escolas_2025_rosario = escolas_2025[
        (escolas_2025["id_municipio"].astype(str) == ID_MUNICIPIO_ROSARIO)
        & (escolas_2025["rede"] == "municipal")
    ]

    municipios = pd.concat([municipios_2023, municipios_2025], ignore_index=True)
    escolas_rosario = pd.concat([escolas_2023, escolas_2025_rosario], ignore_index=True)

    ranking_estadual, ranking_dre4 = adicionar_rankings(municipios)

    rosario_municipio = municipios[municipios["id_municipio"].astype(str) == ID_MUNICIPIO_ROSARIO]
    comparativo_rosario = calcular_variacoes(
        rosario_municipio,
        ["id_municipio", "municipio", "anos_escolares"],
    )

    pos_est = ranking_estadual[
        ranking_estadual["id_municipio"].astype(str) == ID_MUNICIPIO_ROSARIO
    ][["ano", "anos_escolares", "posicao_estadual"]]
    pos_dre4 = ranking_dre4[
        ranking_dre4["id_municipio"].astype(str) == ID_MUNICIPIO_ROSARIO
    ][["ano", "anos_escolares", "posicao_dre4"]]

    for ano in [2023, 2025]:
        comparativo_rosario = comparativo_rosario.merge(
            pos_est[pos_est["ano"] == ano]
            .drop(columns="ano")
            .rename(columns={"posicao_estadual": f"posicao_estadual_{ano}"}),
            on="anos_escolares",
            how="left",
        )
        comparativo_rosario = comparativo_rosario.merge(
            pos_dre4[pos_dre4["ano"] == ano]
            .drop(columns="ano")
            .rename(columns={"posicao_dre4": f"posicao_dre4_{ano}"}),
            on="anos_escolares",
            how="left",
        )

    comparativo_rosario["mudanca_posicao_estadual"] = (
        comparativo_rosario["posicao_estadual_2023"]
        - comparativo_rosario["posicao_estadual_2025"]
    )
    comparativo_rosario["mudanca_posicao_dre4"] = (
        comparativo_rosario["posicao_dre4_2023"]
        - comparativo_rosario["posicao_dre4_2025"]
    )

    comparativo_escolas = calcular_variacoes(
        escolas_rosario,
        ["id_municipio", "id_escola", "anos_escolares"],
    )
    nomes_escolas = (
        escolas_rosario.sort_values("ano")
        .groupby("id_escola", as_index=False)["escola"]
        .last()
    )
    comparativo_escolas = comparativo_escolas.merge(
        nomes_escolas,
        on="id_escola",
        how="left",
    )
    colunas_escola = ["id_municipio", "id_escola", "escola", "anos_escolares"]
    comparativo_escolas = comparativo_escolas[
        colunas_escola + [col for col in comparativo_escolas.columns if col not in colunas_escola]
    ]
    comparativo_escolas["classificacao_variacao"] = "estabilidade"
    comparativo_escolas.loc[
        comparativo_escolas["variacao_absoluta"] > 0, "classificacao_variacao"
    ] = "avanco"
    comparativo_escolas.loc[
        comparativo_escolas["variacao_absoluta"] < 0, "classificacao_variacao"
    ] = "queda"

    dre4_variacao = calcular_variacoes(
        ranking_dre4,
        ["id_municipio", "municipio", "municipio_dre4", "anos_escolares"],
    )

    saidas = {
        "comparativo_rosario": comparativo_rosario,
        "comparativo_escolas": comparativo_escolas,
        "ranking_estadual": ranking_estadual.sort_values(
            ["ano", "anos_escolares", "posicao_estadual"]
        ),
        "ranking_dre4": ranking_dre4.sort_values(["ano", "anos_escolares", "posicao_dre4"]),
        "dre4_variacao": dre4_variacao.sort_values(["anos_escolares", "variacao_absoluta"], ascending=[True, False]),
        "sergipe_2023_oficial": sergipe_2023,
    }

    for nome, df in saidas.items():
        df.to_csv(TABELAS_DIR / f"{nome}.csv", index=False, encoding="utf-8-sig")
    salvar_excel(saidas, TABELAS_DIR / "analise_ideb_rosario_2023_2025.xlsx")

    print("Analise historica concluida.")
    print(comparativo_rosario[[
        "anos_escolares",
        "ideb_2023",
        "ideb_2025",
        "variacao_absoluta",
        "variacao_percentual",
        "posicao_estadual_2023",
        "posicao_estadual_2025",
        "posicao_dre4_2023",
        "posicao_dre4_2025",
    ]].to_string(index=False))
    print(f"Tabelas salvas em: {TABELAS_DIR}")


if __name__ == "__main__":
    main()
