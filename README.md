# Analise IDEB - Rosario do Catete

Projeto para analisar o IDEB 2023 x 2025 com foco em Rosario do Catete/SE.

## Escopo

- Municipio foco: Rosario do Catete
- Comparacoes: DRE 4, ranking estadual dos municipios e escolas municipais
- Anos: 2023 e 2025
- Etapas: anos iniciais e anos finais
- Produtos: tabelas, graficos, relatorios e exportacoes CSV/XLSX

## DRE 4

Municipios considerados:

- Capela
- Carmopolis
- Divina Pastora
- General Maynard
- Japaratuba
- Pirambu
- Rosario do Catete
- Santa Rosa de Lima
- Siriri

## Primeiro passo

Rode a exploracao do BigQuery para confirmar:

- quais tabelas existem em `basedosdados.br_inep_ideb`;
- quais colunas existem;
- se a tabela `brasil` ja contem 2025;
- qual e o formato real dos registros.

```powershell
cd .\ideb_rosario_catete
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Necessario uma vez, se voce usa Google Cloud CLI:
gcloud auth application-default login

python main.py
```

Por padrao, o projeto usa `cosmic-attic-499623-i4` como projeto de billing do
BigQuery. Para alterar:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "seu-projeto"
```

Se o comando `gcloud` nao existir, instale o Google Cloud CLI ou use uma chave de
service account:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\caminho\para\sua-chave.json"
python main.py
```

## Saidas esperadas

As consultas exploratorias salvam arquivos em `data/raw/`:

- `bigquery_tabelas.csv`
- `bigquery_colunas.csv`
- `bigquery_anos.csv`
- `bigquery_amostra_2023_2025.csv`

Depois de confirmar colunas e anos, os SQLs definitivos serao preenchidos para
municipio, DRE 4/ranking estadual e escolas.
## Pipeline com os arquivos 2025

Como as planilhas oficiais 2025 ja estao em `data/raw/`, rode:

```powershell
python main.py
```

Esse comando processa as planilhas 2025 e gera as tabelas comparativas em
`outputs/tabelas/`.

Comandos especificos:

```powershell
python main.py --explorar      # refaz a exploracao do BigQuery
python main.py --tratar-2025   # reprocessa apenas as planilhas 2025
python main.py --analise       # refaz apenas as tabelas 2023 x 2025
```

Principais tabelas geradas:

- `comparativo_rosario.csv`
- `comparativo_escolas.csv`
- `ranking_estadual.csv`
- `ranking_dre4.csv`
- `dre4_variacao.csv`
- `analise_ideb_rosario_2023_2025.xlsx`
## Apresentacao executiva PowerPoint

Para gerar a apresentacao executiva completa:

```powershell
python generate_presentation.py
```

Saida principal:

- `outputs/apresentacao/IDEB_Rosario_do_Catete_2023_2025.pptx`

Arquivos auxiliares:

- `outputs/graficos_apresentacao/`
- `outputs/tabelas_apresentacao/`
## Apresentacao web interativa

A versao web fica em:

- `web/index.html`
- `web/dist/index.html` como arquivo standalone portatil

Para abrir diretamente, use `web/index.html`. Se preferir servir pelo navegador:

```powershell
python -m http.server 8000
```

Depois acesse:

```text
http://localhost:8000/web/
```

Para regerar o JSON central depois de atualizar tabelas:

```powershell
python generate_web_data.py
python build_web_dist.py
```