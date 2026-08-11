from __future__ import annotations

import pandas as pd


def classificar_variacao_escolas(
    df: pd.DataFrame,
    *,
    coluna_variacao: str = "variacao_absoluta",
) -> pd.DataFrame:
    resultado = df.copy()
    resultado["classificacao_variacao"] = "estabilidade"
    resultado.loc[resultado[coluna_variacao] > 0, "classificacao_variacao"] = "avanco"
    resultado.loc[resultado[coluna_variacao] < 0, "classificacao_variacao"] = "queda"
    return resultado


def escolas_que_mais_avancaram(
    df: pd.DataFrame,
    *,
    coluna_variacao: str = "variacao_absoluta",
    limite: int = 10,
) -> pd.DataFrame:
    return df.sort_values(coluna_variacao, ascending=False).head(limite)
