from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TABLES_DIR = OUTPUT_DIR / "tabelas"
PRESENTATION_DIR = OUTPUT_DIR / "apresentacao"
CHARTS_DIR = OUTPUT_DIR / "graficos_apresentacao"
PRESENTATION_TABLES_DIR = OUTPUT_DIR / "tabelas_apresentacao"
PPTX_PATH = PRESENTATION_DIR / "IDEB_Rosario_do_Catete_2023_2025.pptx"
TEMP_PPTX_PATH = PRESENTATION_DIR / "IDEB_Rosario_do_Catete_2023_2025.tmp.pptx"
LOGO_PATH = PROJECT_ROOT / "logo_semed.png"

MUNICIPIO = "Rosario do Catete"
MUNICIPIO_DISPLAY = "Rosario do Catete"
UF = "SE"
ANOS = [2023, 2025]
REDE = "municipal"
DRE4 = [
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
ID_MUNICIPIO_ROSARIO = "2806107"

SLIDE_W = 13.333
SLIDE_H = 7.5
SAFE_X = 0.55
SAFE_Y = 0.38

COLORS = {
    "navy": "35478D",
    "cyan": "32A9ED",
    "magenta": "FA2B6C",
    "yellow": "FFC928",
    "aqua": "40CDB6",
    "support_blue": "287FB6",
    "dark_text": "4E5662",
    "mid_gray": "9AA0A6",
    "light_gray": "E8EBEF",
    "white": "FFFFFF",
    "soft_bg": "F7F9FC",
}

MPL_COLORS = {key: f"#{value}" for key, value in COLORS.items()}
FONT = "Aptos"
SOURCE_TEXT = "Fonte: INEP / IDEB / Base dos Dados | Elaboracao: analise propria | IDEB 2023-2025"
