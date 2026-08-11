from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import CHARTS_DIR, ID_MUNICIPIO_ROSARIO, MPL_COLORS
from .metrics import fmt_num, fmt_pct

plt.rcParams["font.family"] = "Arial"
plt.rcParams["figure.dpi"] = 130
plt.rcParams["savefig.dpi"] = 240


def setup_ax(ax):
    ax.set_facecolor("white")
    ax.grid(axis="x", color=MPL_COLORS["light_gray"], linewidth=0.8)
    ax.grid(axis="y", visible=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=MPL_COLORS["dark_text"], labelsize=9)


def save_chart(fig, filename: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / filename
    fig.savefig(path, bbox_inches="tight", facecolor="white", transparent=False)
    plt.close(fig)
    return path


def slug(text: str) -> str:
    return text.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")


def chart_summary_bars(metrics: dict) -> Path:
    df = metrics["rosario"].copy().sort_values("etapa")
    labels = df["etapa"].tolist()
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    bars1 = ax.bar(x - width / 2, df["ideb_2023"], width, color=MPL_COLORS["mid_gray"], label="2023")
    bars2 = ax.bar(x + width / 2, df["ideb_2025"], width, color=MPL_COLORS["cyan"], label="2025")
    ax.set_ylim(0, 10)
    ax.set_xticks(x, labels)
    ax.set_ylabel("IDEB", color=MPL_COLORS["dark_text"])
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    setup_ax(ax)
    for bars in [bars1, bars2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.12, fmt_num(bar.get_height()), ha="center", va="bottom", fontsize=10, color=MPL_COLORS["navy"], fontweight="bold")
    return save_chart(fig, "01_resumo_executivo.png")


def chart_dumbbell_stage(metrics: dict, stage: str, filename: str) -> Path:
    row = metrics["rosario"][metrics["rosario"]["etapa"] == stage].iloc[0]
    fig, ax = plt.subplots(figsize=(9.6, 3.1))
    y = 0
    ax.hlines(y, row["ideb_2023"], row["ideb_2025"], color=MPL_COLORS["light_gray"], linewidth=8, zorder=1)
    ax.scatter(row["ideb_2023"], y, s=520, color=MPL_COLORS["navy"], zorder=3)
    ax.scatter(row["ideb_2025"], y, s=620, color=MPL_COLORS["cyan"], zorder=4)
    ax.text(row["ideb_2023"], y, fmt_num(row["ideb_2023"]), ha="center", va="center", color="white", fontweight="bold", fontsize=13)
    ax.text(row["ideb_2025"], y, fmt_num(row["ideb_2025"]), ha="center", va="center", color="white", fontweight="bold", fontsize=13)
    ax.text(row["ideb_2023"], y - 0.38, "2023", ha="center", color=MPL_COLORS["dark_text"], fontsize=10)
    ax.text(row["ideb_2025"], y - 0.38, "2025", ha="center", color=MPL_COLORS["dark_text"], fontsize=10)
    ax.text((row["ideb_2023"] + row["ideb_2025"]) / 2, y + 0.5, f"{fmt_num(row['variacao_absoluta'], signed=True)} ponto | {fmt_pct(row['variacao_percentual'])}", ha="center", color=MPL_COLORS["aqua"], fontweight="bold", fontsize=12)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.95, 0.95)
    ax.set_yticks([])
    ax.set_xlabel("Escala IDEB 0 a 10", color=MPL_COLORS["mid_gray"], fontsize=9)
    setup_ax(ax)
    return save_chart(fig, filename)


def chart_rosario_vs_sergipe(metrics: dict, stage: str, filename: str) -> Path:
    ros = metrics["rosario"][metrics["rosario"]["etapa"] == stage].iloc[0]
    ser = metrics["media_sergipe"][metrics["media_sergipe"]["etapa"] == stage]
    values = []
    for ano in [2023, 2025]:
        values.append({"ano": str(ano), "ref": "Rosario", "ideb": ros[f"ideb_{ano}"]})
        values.append({"ano": str(ano), "ref": "Media municipal SE", "ideb": ser[ser["ano"] == ano]["ideb"].iloc[0]})
    df = pd.DataFrame(values)
    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    x = np.arange(2)
    width = 0.34
    ros_vals = df[df["ref"] == "Rosario"]["ideb"].to_numpy()
    se_vals = df[df["ref"] == "Media municipal SE"]["ideb"].to_numpy()
    b1 = ax.bar(x - width / 2, ros_vals, width, color=MPL_COLORS["navy"], label="Rosario")
    b2 = ax.bar(x + width / 2, se_vals, width, color="#A7ADB5", label="Media municipal SE")
    ax.set_ylim(0, 10)
    ax.set_xticks(x, ["2023", "2025"])
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    setup_ax(ax)
    for bars in [b1, b2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.12, fmt_num(bar.get_height()), ha="center", fontweight="bold", fontsize=10, color=MPL_COLORS["navy"])
    diff = ros_vals[-1] - se_vals[-1]
    ax.text(1, max(ros_vals[-1], se_vals[-1]) + 0.75, f"Diferenca 2025: {fmt_num(diff, signed=True)}", ha="center", color=MPL_COLORS["magenta"] if diff < 0 else MPL_COLORS["aqua"], fontweight="bold")
    return save_chart(fig, filename)


def chart_dre4_ranking(metrics: dict, stage: str, filename: str) -> Path:
    df = metrics["ranking_dre4_seq"][(metrics["ranking_dre4_seq"]["ano"] == 2025) & (metrics["ranking_dre4_seq"]["etapa"] == stage)].copy()
    df = df.sort_values("ranking_seq", ascending=False)
    colors = [MPL_COLORS["magenta"] if x == ID_MUNICIPIO_ROSARIO else MPL_COLORS["navy"] for x in df["id_municipio"]]
    fig, ax = plt.subplots(figsize=(8.6, 4.9))
    bars = ax.barh(df["municipio_dre4"], df["ideb"], color=colors)
    ax.set_xlim(0, 10)
    setup_ax(ax)
    for bar, (_, row) in zip(bars, df.iterrows()):
        ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2, f"{int(row['ranking_seq'])}o | {fmt_num(row['ideb'])}", va="center", fontsize=9, color=MPL_COLORS["dark_text"], fontweight="bold" if row["id_municipio"] == ID_MUNICIPIO_ROSARIO else "normal")
    ax.set_xlabel("IDEB 2025", color=MPL_COLORS["mid_gray"])
    return save_chart(fig, filename)


def chart_dre4_variation(metrics: dict, stage: str, filename: str) -> Path:
    df = metrics["dre4_variacao"][metrics["dre4_variacao"]["etapa"] == stage].copy().sort_values("variacao_absoluta")
    colors = []
    for _, row in df.iterrows():
        if row["id_municipio"] == ID_MUNICIPIO_ROSARIO:
            colors.append(MPL_COLORS["magenta"])
        elif row["variacao_absoluta"] >= 0:
            colors.append(MPL_COLORS["aqua"])
        else:
            colors.append(MPL_COLORS["magenta"])
    fig, ax = plt.subplots(figsize=(8.6, 4.9))
    bars = ax.barh(df["municipio_dre4"], df["variacao_absoluta"], color=colors)
    ax.axvline(0, color=MPL_COLORS["dark_text"], linewidth=0.8)
    setup_ax(ax)
    for bar, value in zip(bars, df["variacao_absoluta"]):
        x = value + (0.035 if value >= 0 else -0.035)
        ha = "left" if value >= 0 else "right"
        ax.text(x, bar.get_y() + bar.get_height() / 2, fmt_num(value, signed=True), va="center", ha=ha, fontsize=9, color=MPL_COLORS["dark_text"], fontweight="bold")
    ax.set_xlabel("IDEB 2025 - IDEB 2023", color=MPL_COLORS["mid_gray"])
    return save_chart(fig, filename)


def chart_state_context(metrics: dict, stage: str, filename: str) -> Path:
    df = metrics["ranking_estadual_seq"][(metrics["ranking_estadual_seq"]["ano"] == 2025) & (metrics["ranking_estadual_seq"]["etapa"] == stage)].copy()
    pos = int(df[df["id_municipio"] == ID_MUNICIPIO_ROSARIO]["ranking_seq"].iloc[0])
    recorte = df[(df["ranking_seq"] >= max(1, pos - 5)) & (df["ranking_seq"] <= pos + 5)].copy().sort_values("ranking_seq", ascending=False)
    colors = [MPL_COLORS["magenta"] if x == ID_MUNICIPIO_ROSARIO else MPL_COLORS["mid_gray"] for x in recorte["id_municipio"]]
    fig, ax = plt.subplots(figsize=(8.6, 4.9))
    bars = ax.barh(recorte["municipio"], recorte["ideb"], color=colors)
    ax.set_xlim(0, 10)
    setup_ax(ax)
    for bar, (_, row) in zip(bars, recorte.iterrows()):
        ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2, f"{int(row['ranking_seq'])}o | {fmt_num(row['ideb'])}", va="center", fontsize=8.5, color=MPL_COLORS["dark_text"])
    ax.set_xlabel("IDEB 2025", color=MPL_COLORS["mid_gray"])
    return save_chart(fig, filename)


def chart_flow_performance(metrics: dict, filename: str) -> Path:
    df = metrics["rosario"].copy()
    fig, ax = plt.subplots(figsize=(7.6, 4.9))
    colors = [MPL_COLORS["cyan"], MPL_COLORS["magenta"]]
    ax.scatter(df["variacao_desempenho"], df["variacao_rendimento"], s=520, c=colors, edgecolor="white", linewidth=2)
    for _, row in df.iterrows():
        ax.text(row["variacao_desempenho"] + 0.015, row["variacao_rendimento"] + 0.004, row["etapa"], fontsize=10, color=MPL_COLORS["navy"], fontweight="bold")
    ax.axhline(0, color=MPL_COLORS["light_gray"], linewidth=1)
    ax.axvline(0, color=MPL_COLORS["light_gray"], linewidth=1)
    ax.set_xlabel("Variacao do desempenho SAEB", color=MPL_COLORS["dark_text"])
    ax.set_ylabel("Variacao do rendimento/fluxo", color=MPL_COLORS["dark_text"])
    setup_ax(ax)
    return save_chart(fig, filename)


def chart_school_dumbbell(metrics: dict, stage: str, filename: str) -> Path:
    df = metrics["escolas_validas"][metrics["escolas_validas"]["etapa"] == stage].copy().sort_values("ideb_2025")
    fig, ax = plt.subplots(figsize=(9.3, 4.9))
    y = np.arange(len(df))
    ax.hlines(y, df["ideb_2023"], df["ideb_2025"], color=MPL_COLORS["light_gray"], linewidth=4)
    ax.scatter(df["ideb_2023"], y, color=MPL_COLORS["navy"], s=90, label="2023")
    ax.scatter(df["ideb_2025"], y, color=MPL_COLORS["cyan"], s=120, label="2025")
    ax.set_yticks(y, [shorten(name) for name in df["escola"]])
    ax.set_xlim(0, 10)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    setup_ax(ax)
    for _, row in df.iterrows():
        yi = list(df.index).index(row.name)
        ax.text(row["ideb_2025"] + 0.08, yi, fmt_num(row["ideb_2025"]), va="center", fontsize=9, color=MPL_COLORS["navy"], fontweight="bold")
    return save_chart(fig, filename)


def chart_school_variation(metrics: dict, filename: str) -> Path:
    df = metrics["escolas_validas"].copy().sort_values("variacao_absoluta")
    df["label"] = df["etapa"].str.replace("Anos ", "") + " | " + df["escola"].map(shorten)
    colors = [MPL_COLORS["aqua"] if value >= 0 else MPL_COLORS["magenta"] for value in df["variacao_absoluta"]]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    bars = ax.barh(df["label"], df["variacao_absoluta"], color=colors)
    ax.axvline(0, color=MPL_COLORS["dark_text"], linewidth=0.8)
    setup_ax(ax)
    for bar, value in zip(bars, df["variacao_absoluta"]):
        ax.text(value + 0.04, bar.get_y() + bar.get_height() / 2, fmt_num(value, signed=True), va="center", fontsize=9, color=MPL_COLORS["dark_text"], fontweight="bold")
    return save_chart(fig, filename)


def chart_ranking_change(metrics: dict, filename: str) -> Path:
    df = metrics["rosario"].copy()
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for _, row in df.iterrows():
        ax.plot([2023, 2025], [row["ranking_estadual_seq_2023"], row["ranking_estadual_seq_2025"]], marker="o", linewidth=3, label=row["etapa"])
        ax.text(2023 - 0.03, row["ranking_estadual_seq_2023"], fmt_rank_plain(row["ranking_estadual_seq_2023"]), ha="right", va="center", fontsize=10, color=MPL_COLORS["navy"], fontweight="bold")
        ax.text(2025 + 0.03, row["ranking_estadual_seq_2025"], fmt_rank_plain(row["ranking_estadual_seq_2025"]), ha="left", va="center", fontsize=10, color=MPL_COLORS["navy"], fontweight="bold")
    ax.invert_yaxis()
    ax.set_xticks([2023, 2025])
    ax.set_ylabel("Posicao estadual", color=MPL_COLORS["dark_text"])
    ax.legend(frameon=False, loc="best")
    setup_ax(ax)
    return save_chart(fig, filename)


def fmt_rank_plain(value) -> str:
    return f"{int(value)}º"


def shorten(name: str, max_len: int = 34) -> str:
    cleaned = str(name).replace("ESCOLA-MUNICIPAL-", "EM ").replace("ESCOLA MUNICIPAL ", "EM ").replace("ESCOLA-MUL-", "EM ")
    cleaned = cleaned.replace("-", " ").replace("  ", " ")
    return cleaned if len(cleaned) <= max_len else cleaned[: max_len - 1] + "..."


def create_all_charts(metrics: dict) -> dict[str, Path]:
    charts = {
        "resumo": chart_summary_bars(metrics),
        "iniciais": chart_dumbbell_stage(metrics, "Anos iniciais", "02_ideb_iniciais.png"),
        "finais": chart_dumbbell_stage(metrics, "Anos finais", "03_ideb_finais.png"),
        "sergipe_iniciais": chart_rosario_vs_sergipe(metrics, "Anos iniciais", "04_rosario_sergipe_iniciais.png"),
        "sergipe_finais": chart_rosario_vs_sergipe(metrics, "Anos finais", "05_rosario_sergipe_finais.png"),
        "dre4_iniciais": chart_dre4_ranking(metrics, "Anos iniciais", "06_ranking_dre4_iniciais.png"),
        "dre4_finais": chart_dre4_ranking(metrics, "Anos finais", "07_ranking_dre4_finais.png"),
        "dre4_var_iniciais": chart_dre4_variation(metrics, "Anos iniciais", "08_variacao_dre4_iniciais.png"),
        "dre4_var_finais": chart_dre4_variation(metrics, "Anos finais", "09_variacao_dre4_finais.png"),
        "ranking_estadual": chart_ranking_change(metrics, "10_ranking_estadual.png"),
        "contexto_estadual_iniciais": chart_state_context(metrics, "Anos iniciais", "11_contexto_estadual_iniciais.png"),
        "contexto_estadual_finais": chart_state_context(metrics, "Anos finais", "12_contexto_estadual_finais.png"),
        "fluxo_desempenho": chart_flow_performance(metrics, "13_desempenho_fluxo.png"),
        "escolas_iniciais": chart_school_dumbbell(metrics, "Anos iniciais", "14_escolas_ideb_iniciais.png"),
        "escolas_finais": chart_school_dumbbell(metrics, "Anos finais", "15_escolas_ideb_finais.png"),
        "variacao_escolas": chart_school_variation(metrics, "16_variacao_escolas.png"),
    }
    return charts
