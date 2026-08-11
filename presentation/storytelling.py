from __future__ import annotations

import pandas as pd

from .metrics import fmt_num, fmt_pct, fmt_rank


def phrase_variation(row) -> str:
    value = row["variacao_absoluta"]
    if value > 0:
        return f"Rosario avancou {fmt_num(value, signed=True)} ponto no IDEB entre 2023 e 2025."
    if value < 0:
        return f"Rosario recuou {fmt_num(value, signed=True)} ponto no IDEB entre 2023 e 2025."
    return "Rosario manteve estabilidade no IDEB entre 2023 e 2025."


def phrase_ranking(row, scope: str = "estadual") -> str:
    if scope == "dre4":
        before = row["ranking_dre4_seq_2023"]
        after = row["ranking_dre4_seq_2025"]
        change = row["mudanca_ranking_dre4_seq"]
        label = "na DRE 4"
    else:
        before = row["ranking_estadual_seq_2023"]
        after = row["ranking_estadual_seq_2025"]
        change = row["mudanca_ranking_estadual_seq"]
        label = "no ranking estadual"
    if change > 0:
        return f"Passou da {fmt_rank(before)} para a {fmt_rank(after)} posicao {label}, ganhando {int(change)} posicao." if int(change) == 1 else f"Passou da {fmt_rank(before)} para a {fmt_rank(after)} posicao {label}, ganhando {int(change)} posicoes."
    if change < 0:
        return f"Passou da {fmt_rank(before)} para a {fmt_rank(after)} posicao {label}, perdendo {abs(int(change))} posicao." if abs(int(change)) == 1 else f"Passou da {fmt_rank(before)} para a {fmt_rank(after)} posicao {label}, perdendo {abs(int(change))} posicoes."
    return f"Manteve a {fmt_rank(after)} posicao {label}."


def driver_flow(row) -> str:
    perf = row["variacao_desempenho"]
    fluxo = row["variacao_rendimento"]
    if abs(perf) > abs(fluxo) * 2:
        return "O avanco foi impulsionado principalmente pelo desempenho."
    if abs(fluxo) > abs(perf) * 2:
        return "O crescimento ocorreu principalmente pelo aumento do fluxo."
    return "Desempenho e fluxo contribuiram conjuntamente para o resultado."


def title_for_stage(row) -> str:
    if row["variacao_absoluta"] > 0:
        return f"{row['etapa']} avancam no IDEB"
    if row["variacao_absoluta"] < 0:
        return f"{row['etapa']} exigem atencao"
    return f"{row['etapa']} mantem estabilidade"


def executive_highlights(metrics: dict) -> list[str]:
    ros = metrics["rosario"].copy()
    schools = metrics["escolas_validas"]
    highlights = []
    best_stage = ros.sort_values("variacao_absoluta", ascending=False).iloc[0]
    highlights.append(f"Maior crescimento nos {best_stage['etapa']}: {fmt_num(best_stage['variacao_absoluta'], signed=True)} ponto.")
    dre_best = ros.sort_values("ranking_dre4_seq_2025").iloc[0]
    highlights.append(f"Melhor posicao regional: {fmt_rank(dre_best['ranking_dre4_seq_2025'])} lugar na DRE 4 nos {dre_best['etapa']}.")
    if len(schools) > 0:
        school = schools.sort_values("variacao_absoluta", ascending=False).iloc[0]
        highlights.append(f"Maior avanco escolar: {school['escola']} ({fmt_num(school['variacao_absoluta'], signed=True)} ponto).")
    count = metrics["contagem_escolas"]
    highlights.append(f"{count['avancaram']} de {count['comparaveis']} resultados escolares comparaveis avancaram.")
    return highlights[:5]


def attention_points(metrics: dict) -> list[str]:
    points = []
    ros = metrics["rosario"].copy()
    for _, row in ros.iterrows():
        if row["mudanca_ranking_estadual_seq"] < 0:
            points.append(f"{row['etapa']}: queda de {abs(int(row['mudanca_ranking_estadual_seq']))} posicoes no ranking estadual.")
        if row["variacao_desempenho"] < 0:
            points.append(f"{row['etapa']}: desempenho SAEB recuou no periodo.")
        if row["variacao_rendimento"] < 0:
            points.append(f"{row['etapa']}: fluxo/rendimento recuou no periodo.")
    count = metrics["contagem_escolas"]
    if count["recuaram"] > 0:
        points.append(f"{count['recuaram']} resultados escolares comparaveis apresentaram queda.")
    if not points:
        points.append("Nao ha recuos de IDEB entre os resultados comparaveis; a gestao deve focar sustentacao e reducao de desigualdades entre escolas.")
    return points[:5]


def priorities(metrics: dict) -> list[str]:
    ros = metrics["rosario"]
    weaker = ros.sort_values("ideb_2025").iloc[0]
    points = [
        f"Intensificar acompanhamento dos {weaker['etapa']}, etapa com menor IDEB 2025.",
        "Monitorar aprendizagem e fluxo conjuntamente em cada ciclo avaliativo.",
        "Disseminar praticas das escolas com maior crescimento.",
        "Apoiar escolas e etapas com menor desempenho relativo.",
        "Usar rankings DRE 4 e estadual como instrumentos de gestao, nao como fim em si mesmos.",
    ]
    return points
