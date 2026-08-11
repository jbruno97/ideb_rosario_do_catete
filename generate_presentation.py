from __future__ import annotations

from presentation.charts import create_all_charts
from presentation.config import CHARTS_DIR, PPTX_PATH, TEMP_PPTX_PATH, PRESENTATION_TABLES_DIR
from presentation.data_loader import load_data
from presentation.metrics import build_metrics
from presentation.slides import create_presentation
from presentation.validation import validate_data, validate_presentation


def main() -> None:
    print("[1/8] Carregando dados...")
    data = load_data()

    print("[2/8] Calculando indicadores...")
    metrics = build_metrics(data)

    print("[3/8] Validando dados...")
    warnings = validate_data(data, metrics)
    for warning in warnings:
        print(f"Aviso: {warning}")

    print("[4/8] Criando graficos...")
    charts = create_all_charts(metrics)

    print("[5/8] Criando narrativa...")
    # A narrativa e gerada dentro dos slides a partir de metrics/storytelling.

    print("[6/8] Montando slides...")
    _, slide_count = create_presentation(metrics, charts)

    print("[7/8] Validando apresentacao...")
    validate_presentation(TEMP_PPTX_PATH, slide_count, charts)

    if PPTX_PATH.exists():
        PPTX_PATH.unlink()
    TEMP_PPTX_PATH.replace(PPTX_PATH)

    print("[8/8] Apresentacao concluida.")
    print(f"Apresentacao criada: {PPTX_PATH}")
    print(f"Slides: {slide_count}")
    print(f"Graficos: {len(charts)} em {CHARTS_DIR}")
    print(f"Tabelas: {PRESENTATION_TABLES_DIR}")


if __name__ == "__main__":
    main()
