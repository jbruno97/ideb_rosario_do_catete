from __future__ import annotations

import pandas as pd

from .config import DRE4, ID_MUNICIPIO_ROSARIO


def validate_data(data: dict[str, pd.DataFrame], metrics: dict) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    rosario = metrics["rosario"]
    escolas = metrics["escolas_validas"]
    ranking = metrics["ranking_estadual_seq"]
    dre4 = metrics["ranking_dre4_seq"]

    if set(rosario["anos_escolares"]) != {"iniciais (1-5)", "finais (6-9)"}:
        errors.append("Rosario nao possui exatamente as duas etapas esperadas.")
    for ano in [2023, 2025]:
        for col in [f"ideb_{ano}", f"indicador_rendimento_{ano}", f"nota_saeb_media_padronizada_{ano}"]:
            if col not in rosario.columns or rosario[col].isna().any():
                errors.append(f"Indicador ausente em Rosario: {col}.")

    if rosario["id_municipio"].astype(str).nunique() != 1 or rosario["id_municipio"].astype(str).iloc[0] != ID_MUNICIPIO_ROSARIO:
        errors.append("Rosario do Catete nao esta identificado pelo id_municipio 2806107.")

    if escolas.duplicated(["id_escola", "anos_escolares"]).any():
        errors.append("Ha duplicacao no comparativo de escolas por id_escola e etapa.")
    if len(escolas) == 0:
        errors.append("Nao ha escolas com IDEB comparavel entre 2023 e 2025.")

    for ano in [2023, 2025]:
        for etapa in ["iniciais (1-5)", "finais (6-9)"]:
            subset = ranking[(ranking["ano"] == ano) & (ranking["anos_escolares"] == etapa)]
            if subset["id_municipio"].nunique() != 75:
                warnings.append(f"Ranking estadual {ano} {etapa} possui {subset['id_municipio'].nunique()} municipios, esperado 75.")
            dre_subset = dre4[(dre4["ano"] == ano) & (dre4["anos_escolares"] == etapa)]
            present = set(dre_subset["municipio_dre4"].dropna())
            missing = set(DRE4) - present
            if missing:
                warnings.append(f"Municipios sem IDEB disponivel na DRE 4 {ano} {etapa}: {sorted(missing)}")

    numeric_cols = ["ideb_2023", "ideb_2025", "variacao_absoluta", "variacao_percentual"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(rosario[col]):
            errors.append(f"Coluna numerica invalida: {col}.")

    if errors:
        raise ValueError("Validacao falhou:\n- " + "\n- ".join(errors))
    return warnings


def validate_presentation(path, slide_count: int, image_paths: dict) -> None:
    if not path.exists():
        raise FileNotFoundError(f"PPTX nao foi criado: {path}")
    if slide_count < 20:
        raise ValueError(f"Apresentacao possui apenas {slide_count} slides.")
    missing = [str(p) for p in image_paths.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Imagens ausentes:\n" + "\n".join(missing))
