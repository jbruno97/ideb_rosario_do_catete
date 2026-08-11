from __future__ import annotations

import pandas as pd

from .config import TABLES_DIR


def load_data() -> dict[str, pd.DataFrame]:
    data = {
        "rosario": pd.read_csv(TABLES_DIR / "comparativo_rosario.csv", dtype={"id_municipio": str}),
        "escolas": pd.read_csv(TABLES_DIR / "comparativo_escolas.csv", dtype={"id_municipio": str, "id_escola": str}),
        "ranking_dre4": pd.read_csv(TABLES_DIR / "ranking_dre4.csv", dtype={"id_municipio": str}),
        "ranking_estadual": pd.read_csv(TABLES_DIR / "ranking_estadual.csv", dtype={"id_municipio": str}),
        "dre4_variacao": pd.read_csv(TABLES_DIR / "dre4_variacao.csv", dtype={"id_municipio": str}),
    }
    return data
