from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MUNICIPIOS_DRE4 = [
    "Capela",
    "Carmopolis",
    "Divina Pastora",
    "General Maynard",
    "Japaratuba",
    "Pirambu",
    "Rosario do Catete",
    "Santa Rosa de Lima",
    "Siriri",
]

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

ID_MUNICIPIO_ROSARIO = "2806107"
COLUNAS_NUMERICAS = [
    "taxa_aprovacao",
    "indicador_rendimento",
    "nota_saeb_matematica",
    "nota_saeb_lingua_portuguesa",
    "nota_saeb_media_padronizada",
    "ideb",
    "projecao",
]

PLANILHAS_2025 = [
    {
        "arquivo": "divulgacao_anos_iniciais_municipios_2025.xlsx",
        "nivel": "municipio",
        "anos_escolares": "iniciais (1-5)",
    },
    {
        "arquivo": "divulgacao_anos_finais_municipios_2025.xlsx",
        "nivel": "municipio",
        "anos_escolares": "finais (6-9)",
    },
    {
        "arquivo": "divulgacao_anos_iniciais_escolas_2025.xlsx",
        "nivel": "escola",
        "anos_escolares": "iniciais (1-5)",
    },
    {
        "arquivo": "divulgacao_anos_finais_escolas_2025.xlsx",
        "nivel": "escola",
        "anos_escolares": "finais (6-9)",
    },
]


def normalizar_texto(valor: object) -> str:
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return " ".join(texto.strip().split()).casefold()


def codigo_texto(valor: object) -> str | None:
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto


def numero(valor: object) -> float | None:
    if pd.isna(valor) or valor == "-":
        return None
    return pd.to_numeric(valor, errors="coerce")


def carregar_csv(nome: str) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / nome)


def validar_disponibilidade_2025() -> bool:
    anos = carregar_csv("bigquery_anos.csv")
    return 2025 in set(anos["ano"].astype(int))


def ler_planilha_inep_2025(config: dict[str, str]) -> pd.DataFrame:
    caminho = RAW_DIR / config["arquivo"]
    df = pd.read_excel(caminho, header=9, dtype=object)

    colunas = {
        "SG_UF": "sigla_uf",
        "CO_MUNICIPIO": "id_municipio",
        "NO_MUNICIPIO": "municipio",
        "REDE": "rede",
        "VL_APROVACAO_2025_SI_4": "taxa_aprovacao",
        "VL_INDICADOR_REND_2025": "indicador_rendimento",
        "VL_NOTA_MATEMATICA_2025": "nota_saeb_matematica",
        "VL_NOTA_PORTUGUES_2025": "nota_saeb_lingua_portuguesa",
        "VL_NOTA_MEDIA_2025": "nota_saeb_media_padronizada",
        "VL_OBSERVADO_2025": "ideb",
    }

    if config["nivel"] == "escola":
        colunas.update({"ID_ESCOLA": "id_escola", "NO_ESCOLA": "escola"})

    saida = df[list(colunas)].rename(columns=colunas).copy()
    saida.insert(0, "ano", 2025)
    saida["ensino"] = "fundamental"
    saida["anos_escolares"] = config["anos_escolares"]
    saida["projecao"] = pd.NA

    saida["id_municipio"] = saida["id_municipio"].map(codigo_texto)
    if "id_escola" in saida.columns:
        saida["id_escola"] = saida["id_escola"].map(codigo_texto)

    saida["rede"] = saida["rede"].map(normalizar_texto)
    for coluna in COLUNAS_NUMERICAS:
        saida[coluna] = saida[coluna].map(numero)

    return saida


def processar_2025() -> tuple[pd.DataFrame, pd.DataFrame]:
    tabelas = [ler_planilha_inep_2025(config) for config in PLANILHAS_2025]
    municipios = pd.concat(
        [df for df, config in zip(tabelas, PLANILHAS_2025) if config["nivel"] == "municipio"],
        ignore_index=True,
    )
    escolas = pd.concat(
        [df for df, config in zip(tabelas, PLANILHAS_2025) if config["nivel"] == "escola"],
        ignore_index=True,
    )
    return municipios, escolas


def salvar_processados(municipios: pd.DataFrame, escolas: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    municipios.to_csv(PROCESSED_DIR / "ideb_2025_municipios.csv", index=False, encoding="utf-8-sig")
    escolas.to_csv(PROCESSED_DIR / "ideb_2025_escolas.csv", index=False, encoding="utf-8-sig")

    municipios_rosario = municipios[
        (municipios["id_municipio"] == ID_MUNICIPIO_ROSARIO)
        & (municipios["rede"] == "municipal")
    ]
    escolas_rosario = escolas[
        (escolas["id_municipio"] == ID_MUNICIPIO_ROSARIO)
        & (escolas["rede"] == "municipal")
    ]
    dre4 = municipios[
        municipios["id_municipio"].isin(IDS_MUNICIPIOS_DRE4)
        & (municipios["rede"] == "municipal")
    ].copy()
    dre4["municipio_dre4"] = dre4["id_municipio"].map(IDS_MUNICIPIOS_DRE4)

    municipios_rosario.to_csv(
        PROCESSED_DIR / "ideb_2025_rosario_municipio.csv",
        index=False,
        encoding="utf-8-sig",
    )
    escolas_rosario.to_csv(
        PROCESSED_DIR / "ideb_2025_rosario_escolas.csv",
        index=False,
        encoding="utf-8-sig",
    )
    dre4.to_csv(PROCESSED_DIR / "ideb_2025_dre4.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    municipios, escolas = processar_2025()
    salvar_processados(municipios, escolas)
    rosario = municipios[
        (municipios["id_municipio"] == ID_MUNICIPIO_ROSARIO)
        & (municipios["rede"] == "municipal")
    ]

    print("Planilhas 2025 processadas.")
    print(f"Municipios: {len(municipios):,} linhas")
    print(f"Escolas: {len(escolas):,} linhas")
    print("Rosario do Catete 2025 - rede municipal:")
    print(rosario[["anos_escolares", "taxa_aprovacao", "indicador_rendimento", "nota_saeb_media_padronizada", "ideb"]].to_string(index=False))
    print(f"Arquivos salvos em: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
