from __future__ import annotations

import argparse
import runpy
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SCRIPTS = {
    "explorar": PROJECT_ROOT / "src" / "01_extracao.py",
    "tratar_2025": PROJECT_ROOT / "src" / "02_tratamento.py",
    "analise": PROJECT_ROOT / "src" / "03_analise_historica.py",
    "graficos": PROJECT_ROOT / "src" / "06_graficos.py",
}
PLANILHAS_2025 = [
    RAW_DIR / "divulgacao_anos_iniciais_municipios_2025.xlsx",
    RAW_DIR / "divulgacao_anos_finais_municipios_2025.xlsx",
    RAW_DIR / "divulgacao_anos_iniciais_escolas_2025.xlsx",
    RAW_DIR / "divulgacao_anos_finais_escolas_2025.xlsx",
]


def executar(nome: str) -> None:
    script = SCRIPTS[nome]
    print(f"\n== {nome}: {script.name} ==")
    runpy.run_path(str(script), run_name="__main__")


def tem_planilhas_2025() -> bool:
    return all(caminho.exists() for caminho in PLANILHAS_2025)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline IDEB Rosario do Catete")
    parser.add_argument("--explorar", action="store_true", help="Roda consultas exploratorias no BigQuery")
    parser.add_argument("--tratar-2025", action="store_true", help="Processa planilhas oficiais 2025 em data/raw")
    parser.add_argument("--analise", action="store_true", help="Gera tabelas 2023 x 2025")
    parser.add_argument("--graficos", action="store_true", help="Gera PNGs, relatorio e apresentacao")
    args = parser.parse_args()

    algum_modo = args.explorar or args.tratar_2025 or args.analise or args.graficos
    if not algum_modo:
        if tem_planilhas_2025():
            args.tratar_2025 = True
            args.analise = True
            args.graficos = True
        else:
            args.explorar = True

    if args.explorar:
        executar("explorar")
    if args.tratar_2025:
        executar("tratar_2025")
    if args.analise:
        executar("analise")
    if args.graficos:
        executar("graficos")


if __name__ == "__main__":
    main()
