# Validacao da apresentacao web

Arquivo principal: web/index.html
Versao standalone: web/dist/index.html
Slides: 22
JSON central: web/data/ideb_data.json
Scripts JS: sintaxe validada com Node

Revisao visual aplicada:

- Capa redesenhada no padrao geometrico da referencia enviada.
- Slides receberam fundo creme, faixas teal/azul/laranja e padrao de pontos.
- Graficos passaram a usar paleta institucional: azul escuro, verde, teal e laranja.
- Rosario do Catete aparece destacado em laranja nos comparativos da DRE 4.
- Cards, tabelas e paineis foram ajustados para visual executivo com sombra suave.
- Slide 04, "O que mudou", reorganizado em cards empilhados/horizontais: etapa, 2023, 2025 e variacao.
- Margens globais foram ampliadas para reduzir interferencia da faixa geometrica esquerda.
- Titulo/subtitulo receberam largura maxima menor para evitar conflito com o padrao de pontos superior direito.
- Rodape recebeu fundo translúcido para preservar legibilidade.
- Versao standalone regenerada com CSS, JS, dados e logo embutidos.

Screenshots de validacao visual:

- web/validation_screenshots/slide_03.png
- web/validation_screenshots/slide_04.png
- web/validation_screenshots/slide_05.png
- web/validation_screenshots/slide_08.png
- web/validation_screenshots/slide_10.png
- web/validation_screenshots/slide_16.png
- web/validation_screenshots/slide_17.png
- web/validation_screenshots/slide_20.png
- web/validation_screenshots/slide_22.png

Interacoes validadas por estrutura:

- Navegacao por teclado
- Navegacao por hash
- Menu lateral de slides
- Botao de tela cheia
- Modal de fonte dos dados
- Barra de progresso
- Contador de slides
- Filtros de etapa em Sergipe/DRE 4/trajetoria
- Filtro de ano no ranking da DRE 4
- Filtros de escolas por status
- Tooltips em graficos SVG

Avisos de dados:

- Alguns municipios da DRE 4 nao possuem IDEB disponivel em determinadas etapas/anos e nao foram tratados como zero.
- Sergipe e representado pela media municipal dos municipios sergipanos com IDEB disponivel.

## Ajuste visual - escala dos graficos (2026-08-10 12:23:35)

- Reduzida a margem/padding geral dos slides analiticos.
- Ampliada a area util dos graficos em slides com chart-panel.
- Reduzidas as margens internas dos SVGs para que o desenho ocupe mais o quadro.
- Recalibrada a altura dos paineis para caber melhor em 1366x768.
- Removida a referencia restante a "Resumo executivo" do menu/comentarios.
- HTML final reconstruido em web/dist/index.html.
- Validacao de sintaxe JavaScript concluida.
