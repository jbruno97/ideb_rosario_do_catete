from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import bigquery


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_BILLING_PROJECT = "cosmic-attic-499623-i4"


QUERIES = {
    "bigquery_tabelas": """
        SELECT
            table_name
        FROM
            `basedosdados.br_inep_ideb.INFORMATION_SCHEMA.TABLES`
        ORDER BY
            table_name
    """,
    "bigquery_colunas": """
        SELECT
            table_name,
            column_name,
            data_type
        FROM
            `basedosdados.br_inep_ideb.INFORMATION_SCHEMA.COLUMNS`
        ORDER BY
            table_name,
            ordinal_position
    """,
    "bigquery_anos": """
        SELECT DISTINCT
            ano
        FROM
            `basedosdados.br_inep_ideb.brasil`
        ORDER BY
            ano DESC
    """,
    "bigquery_amostra_2023_2025": """
        SELECT *
        FROM
            `basedosdados.br_inep_ideb.brasil`
        WHERE
            ano IN (2023, 2025)
        LIMIT 50
    """,
}


def get_client() -> bigquery.Client:
    project = os.getenv("GOOGLE_CLOUD_PROJECT", DEFAULT_BILLING_PROJECT)
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if credentials_path and not Path(credentials_path).exists():
        raise SystemExit(
            "GOOGLE_APPLICATION_CREDENTIALS aponta para um arquivo que nao existe:\n"
            f"{credentials_path}\n\n"
            "Se voce vai usar login pelo Google Cloud CLI, limpe essa variavel:\n"
            "Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS\n\n"
            "Depois autentique com:\n"
            "& \"C:\\Users\\cliente\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd\" auth application-default login"
        )

    try:
        return bigquery.Client(project=project)
    except DefaultCredentialsError as exc:
        raise SystemExit(
            "Credenciais do Google Cloud nao encontradas.\n\n"
            "No seu Windows, rode:\n"
            "& \"C:\\Users\\cliente\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd\" auth application-default login\n\n"
            "Depois rode novamente:\n"
            "python main.py\n\n"
            f"Projeto de billing configurado: {project}"
        ) from exc


def run_query(client: bigquery.Client, query: str) -> pd.DataFrame:
    return client.query(query).result().to_dataframe()


def save_outputs(results: dict[str, pd.DataFrame]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in results.items():
        df.to_csv(RAW_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    client = get_client()
    results = {name: run_query(client, query) for name, query in QUERIES.items()}
    save_outputs(results)

    anos = results["bigquery_anos"]["ano"].tolist()
    print("Consultas exploratorias concluidas.")
    print(f"Anos encontrados: {anos}")
    print(f"Arquivos salvos em: {RAW_DIR}")


if __name__ == "__main__":
    main()
