from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABELAS_DIR = PROJECT_ROOT / "outputs" / "tabelas"
GRAFICOS_DIR = PROJECT_ROOT / "outputs" / "graficos"
RELATORIOS_DIR = PROJECT_ROOT / "outputs" / "relatorios"


ETAPA_LABEL = {
    "iniciais (1-5)": "Anos iniciais",
    "finais (6-9)": "Anos finais",
}


COLORS = {
    "azul": "#2F6B9A",
    "verde": "#2E7D59",
    "amarelo": "#D6A23A",
    "vermelho": "#B85C5C",
    "cinza": "#6B7280",
}


def configurar_tema() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["savefig.dpi"] = 200
    plt.rcParams["font.family"] = "DejaVu Sans"


def salvar(fig: plt.Figure, nome: str) -> Path:
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    caminho = GRAFICOS_DIR / nome
    fig.tight_layout()
    fig.savefig(caminho, bbox_inches="tight")
    plt.close(fig)
    return caminho


def carregar() -> dict[str, pd.DataFrame]:
    return {
        "rosario": pd.read_csv(TABELAS_DIR / "comparativo_rosario.csv"),
        "escolas": pd.read_csv(TABELAS_DIR / "comparativo_escolas.csv"),
        "ranking_dre4": pd.read_csv(TABELAS_DIR / "ranking_dre4.csv"),
        "ranking_estadual": pd.read_csv(TABELAS_DIR / "ranking_estadual.csv"),
        "dre4_variacao": pd.read_csv(TABELAS_DIR / "dre4_variacao.csv"),
    }


def preparar_rosario_longo(rosario: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for _, row in rosario.iterrows():
        for ano in [2023, 2025]:
            linhas.append(
                {
                    "ano": ano,
                    "etapa": ETAPA_LABEL.get(row["anos_escolares"], row["anos_escolares"]),
                    "ideb": row[f"ideb_{ano}"],
                    "rendimento": row[f"indicador_rendimento_{ano}"],
                    "desempenho": row[f"nota_saeb_media_padronizada_{ano}"],
                }
            )
    return pd.DataFrame(linhas)


def grafico_ideb_2023_2025(rosario: pd.DataFrame) -> None:
    df = preparar_rosario_longo(rosario)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.barplot(data=df, x="etapa", y="ideb", hue="ano", palette=[COLORS["cinza"], COLORS["azul"]], ax=ax)
    ax.set_title("IDEB 2023 x 2025 - Rosario do Catete")
    ax.set_xlabel("")
    ax.set_ylabel("IDEB")
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=3)
    ax.bar_label(ax.containers[1], fmt="%.1f", padding=3)
    salvar(fig, "01_ideb_2023_2025_rosario.png")


def grafico_variacao(rosario: pd.DataFrame) -> None:
    df = rosario.copy()
    df["etapa"] = df["anos_escolares"].map(ETAPA_LABEL)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.barplot(data=df, x="etapa", y="variacao_absoluta", color=COLORS["verde"], ax=ax)
    ax.set_title("Crescimento absoluto do IDEB")
    ax.set_xlabel("")
    ax.set_ylabel("Pontos de IDEB")
    ax.bar_label(ax.containers[0], fmt="%+.1f", padding=3)
    salvar(fig, "02_crescimento_absoluto.png")

    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.barplot(data=df, x="etapa", y="variacao_percentual", color=COLORS["amarelo"], ax=ax)
    ax.set_title("Crescimento percentual do IDEB")
    ax.set_xlabel("")
    ax.set_ylabel("% 2023-2025")
    ax.bar_label(ax.containers[0], fmt="%+.1f%%", padding=3)
    salvar(fig, "03_crescimento_percentual.png")


def grafico_fluxo_desempenho(rosario: pd.DataFrame) -> None:
    df = rosario.copy()
    df["etapa"] = df["anos_escolares"].map(ETAPA_LABEL)
    plot = df.melt(
        id_vars="etapa",
        value_vars=["variacao_rendimento", "variacao_desempenho"],
        var_name="indicador",
        value_name="variacao",
    )
    plot["indicador"] = plot["indicador"].replace(
        {
            "variacao_rendimento": "Fluxo/rendimento",
            "variacao_desempenho": "Desempenho SAEB",
        }
    )
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=plot, x="etapa", y="variacao", hue="indicador", palette=[COLORS["verde"], COLORS["azul"]], ax=ax)
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_title("Fluxo x desempenho - origem da variacao")
    ax.set_xlabel("")
    ax.set_ylabel("Variacao 2023-2025")
    salvar(fig, "04_fluxo_x_desempenho.png")


def grafico_dre4(ranking_dre4: pd.DataFrame, dre4_variacao: pd.DataFrame) -> None:
    for etapa, grupo in ranking_dre4[ranking_dre4["ano"] == 2025].groupby("anos_escolares"):
        grupo = grupo.sort_values("posicao_dre4")
        fig, ax = plt.subplots(figsize=(10, 5.5))
        cores = [COLORS["verde"] if x == "2806107" else COLORS["cinza"] for x in grupo["id_municipio"].astype(str)]
        sns.barplot(data=grupo, y="municipio_dre4", x="ideb", palette=cores, hue="municipio_dre4", legend=False, ax=ax)
        ax.set_title(f"Ranking DRE 4 - 2025 - {ETAPA_LABEL.get(etapa, etapa)}")
        ax.set_xlabel("IDEB")
        ax.set_ylabel("")
        salvar(fig, f"05_ranking_dre4_2025_{slug(etapa)}.png")

    df = dre4_variacao.copy()
    df["etapa"] = df["anos_escolares"].map(ETAPA_LABEL)
    for etapa, grupo in df.groupby("etapa"):
        grupo = grupo.sort_values("variacao_absoluta", ascending=False)
        fig, ax = plt.subplots(figsize=(10, 5.5))
        cores = [COLORS["verde"] if x == "2806107" else COLORS["cinza"] for x in grupo["id_municipio"].astype(str)]
        sns.barplot(data=grupo, y="municipio_dre4", x="variacao_absoluta", palette=cores, hue="municipio_dre4", legend=False, ax=ax)
        ax.axvline(0, color="#111827", linewidth=0.8)
        ax.set_title(f"Variacao IDEB DRE 4 - {etapa}")
        ax.set_xlabel("Pontos de IDEB")
        ax.set_ylabel("")
        salvar(fig, f"06_variacao_dre4_{slug(etapa)}.png")


def grafico_ranking_estadual(rosario: pd.DataFrame) -> None:
    df = rosario.copy()
    df["etapa"] = df["anos_escolares"].map(ETAPA_LABEL)
    plot = df.melt(
        id_vars="etapa",
        value_vars=["posicao_estadual_2023", "posicao_estadual_2025"],
        var_name="ano",
        value_name="posicao",
    )
    plot["ano"] = plot["ano"].str.extract(r"(2023|2025)")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.lineplot(data=plot, x="ano", y="posicao", hue="etapa", marker="o", linewidth=2.5, ax=ax)
    ax.invert_yaxis()
    ax.set_title("Posicao estadual de Rosario do Catete")
    ax.set_xlabel("")
    ax.set_ylabel("Posicao no ranking")
    salvar(fig, "07_posicao_estadual_rosario.png")


def grafico_escolas(escolas: pd.DataFrame) -> None:
    df = escolas.copy()
    df["etapa"] = df["anos_escolares"].map(ETAPA_LABEL)
    for etapa, grupo in df.groupby("etapa"):
        ordenado = grupo.sort_values("ideb_2025", ascending=False)
        fig, ax = plt.subplots(figsize=(11, 5.8))
        sns.barplot(data=ordenado, y="escola", x="ideb_2025", color=COLORS["azul"], ax=ax)
        ax.set_title(f"IDEB 2025 por escola municipal - {etapa}")
        ax.set_xlabel("IDEB 2025")
        ax.set_ylabel("")
        salvar(fig, f"08_ideb_escolas_2025_{slug(etapa)}.png")

        ordenado = grupo.sort_values("variacao_absoluta", ascending=False)
        fig, ax = plt.subplots(figsize=(11, 5.8))
        sns.barplot(data=ordenado, y="escola", x="variacao_absoluta", color=COLORS["verde"], ax=ax)
        ax.axvline(0, color="#111827", linewidth=0.8)
        ax.set_title(f"Variacao por escola - {etapa}")
        ax.set_xlabel("Pontos de IDEB")
        ax.set_ylabel("")
        salvar(fig, f"09_variacao_escolas_{slug(etapa)}.png")


def grafico_painel(rosario: pd.DataFrame) -> None:
    df = rosario.copy()
    df["etapa"] = df["anos_escolares"].map(ETAPA_LABEL)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    sns.barplot(data=df, x="etapa", y="ideb_2025", color=COLORS["azul"], ax=axes[0, 0])
    axes[0, 0].set_title("IDEB 2025")
    sns.barplot(data=df, x="etapa", y="variacao_absoluta", color=COLORS["verde"], ax=axes[0, 1])
    axes[0, 1].set_title("Variacao absoluta")
    sns.barplot(data=df, x="etapa", y="posicao_dre4_2025", color=COLORS["amarelo"], ax=axes[1, 0])
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_title("Ranking DRE 4")
    sns.barplot(data=df, x="etapa", y="posicao_estadual_2025", color=COLORS["cinza"], ax=axes[1, 1])
    axes[1, 1].invert_yaxis()
    axes[1, 1].set_title("Ranking estadual")
    for ax in axes.ravel():
        ax.set_xlabel("")
    salvar(fig, "10_painel_executivo_final.png")


def slug(valor: str) -> str:
    return (
        valor.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )


def gerar_relatorio(dados: dict[str, pd.DataFrame]) -> None:
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    r = dados["rosario"].copy()
    iniciais = r[r["anos_escolares"] == "iniciais (1-5)"].iloc[0]
    finais = r[r["anos_escolares"] == "finais (6-9)"].iloc[0]
    texto = f"""# Relatorio executivo - IDEB Rosario do Catete 2023 x 2025

## Sintese

Rosario do Catete avancou nas duas etapas da rede municipal. Nos anos iniciais, o IDEB passou de {iniciais.ideb_2023:.1f} para {iniciais.ideb_2025:.1f}, alta de {iniciais.variacao_absoluta:.1f} ponto ({iniciais.variacao_percentual:.2f}%). Nos anos finais, passou de {finais.ideb_2023:.1f} para {finais.ideb_2025:.1f}, alta de {finais.variacao_absoluta:.1f} ponto ({finais.variacao_percentual:.2f}%).

## Ranking

- Anos iniciais: posicao estadual {int(iniciais.posicao_estadual_2023)} -> {int(iniciais.posicao_estadual_2025)}; DRE 4 {int(iniciais.posicao_dre4_2023)} -> {int(iniciais.posicao_dre4_2025)}.
- Anos finais: posicao estadual {int(finais.posicao_estadual_2023)} -> {int(finais.posicao_estadual_2025)}; DRE 4 {int(finais.posicao_dre4_2023)} -> {int(finais.posicao_dre4_2025)}.

## Diagnostico

- Anos iniciais: variacao do rendimento {iniciais.variacao_rendimento:.3f}; variacao do desempenho {iniciais.variacao_desempenho:.3f}.
- Anos finais: variacao do rendimento {finais.variacao_rendimento:.3f}; variacao do desempenho {finais.variacao_desempenho:.3f}.

## Observacao metodologica

A Base dos Dados continha IDEB ate 2023. Para 2025 foram usadas as planilhas oficiais colocadas em `data/raw/`. O benchmark agregado Rosario x Sergipe 2025 foi retirado do escopo; a comparacao estadual mantida e o ranking dos 75 municipios sergipanos.
"""
    (RELATORIOS_DIR / "relatorio_executivo.md").write_text(texto, encoding="utf-8")

    slides = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>IDEB Rosario do Catete 2023 x 2025</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; color: #111827; background: #f7f7f5; }}
section {{ min-height: 100vh; padding: 48px 64px; box-sizing: border-box; border-bottom: 1px solid #ddd; }}
h1, h2 {{ margin-top: 0; }}
img {{ max-width: 100%; max-height: 72vh; border: 1px solid #ddd; background: white; }}
.big {{ font-size: 36px; line-height: 1.25; }}
</style>
</head>
<body>
<section><h1>IDEB Rosario do Catete</h1><p class="big">Analise 2023 x 2025 da rede municipal, com rankings estadual e DRE 4.</p></section>
<section><h2>Resultado geral</h2><img src="../graficos/01_ideb_2023_2025_rosario.png"></section>
<section><h2>Crescimento absoluto</h2><img src="../graficos/02_crescimento_absoluto.png"></section>
<section><h2>Fluxo x desempenho</h2><img src="../graficos/04_fluxo_x_desempenho.png"></section>
<section><h2>Ranking estadual</h2><img src="../graficos/07_posicao_estadual_rosario.png"></section>
<section><h2>Painel executivo</h2><img src="../graficos/10_painel_executivo_final.png"></section>
</body>
</html>
"""
    (RELATORIOS_DIR / "apresentacao_executiva.html").write_text(slides, encoding="utf-8")


def main() -> None:
    configurar_tema()
    dados = carregar()
    grafico_ideb_2023_2025(dados["rosario"])
    grafico_variacao(dados["rosario"])
    grafico_fluxo_desempenho(dados["rosario"])
    grafico_dre4(dados["ranking_dre4"], dados["dre4_variacao"])
    grafico_ranking_estadual(dados["rosario"])
    grafico_escolas(dados["escolas"])
    grafico_painel(dados["rosario"])
    gerar_relatorio(dados)
    print(f"Graficos salvos em: {GRAFICOS_DIR}")
    print(f"Relatorios salvos em: {RELATORIOS_DIR}")


if __name__ == "__main__":
    main()
