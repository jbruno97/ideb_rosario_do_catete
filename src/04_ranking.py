from __future__ import annotations

import pandas as pd


def adicionar_ranking(
    df: pd.DataFrame,
    *,
    grupo: list[str],
    coluna_ano: str,
    coluna_ideb: str,
    coluna_ranking: str = "posicao",
) -> pd.DataFrame:
    ordenado = df.sort_values([coluna_ano, coluna_ideb], ascending=[True, False]).copy()
    ordenado[coluna_ranking] = (
        ordenado.groupby(grupo + [coluna_ano])[coluna_ideb]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    return ordenado


def calcular_mudanca_posicao(
    df: pd.DataFrame,
    *,
    grupo: list[str],
    coluna_ano: str = "ano",
    coluna_posicao: str = "posicao",
) -> pd.DataFrame:
    tabela = df[df[coluna_ano].isin([2023, 2025])].pivot_table(
        index=grupo,
        columns=coluna_ano,
        values=coluna_posicao,
    )
    tabela = tabela.rename(columns={2023: "posicao_2023", 2025: "posicao_2025"})
    tabela = tabela.reset_index()
    tabela["mudanca_posicao"] = tabela["posicao_2023"] - tabela["posicao_2025"]
    return tabela
