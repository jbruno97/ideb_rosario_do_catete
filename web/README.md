# Apresentacao Web IDEB Rosario do Catete

## Como abrir

Abra diretamente:

```text
web/index.html
```

Se o navegador bloquear recursos locais, rode um servidor simples na raiz do projeto:

```powershell
python -m http.server 8000
```

Depois acesse:

```text
http://localhost:8000/web/
```

## Como apresentar

- Setas esquerda/direita: navegar slides
- PageUp/PageDown: navegar slides
- Espaço: proximo slide
- Home: primeiro slide
- End: ultimo slide
- Botao Apresentar: tela cheia
- Botao Fonte: metodologia e fonte dos dados
- Menu: lista clicavel de slides

## PDF

Use Ctrl+P no navegador e selecione "Salvar como PDF". O CSS de impressao coloca cada slide em uma pagina.

## Regerar dados

1. Atualize as tabelas em `outputs/tabelas/`.
2. Rode:

```powershell
python generate_web_data.py
```

3. Reabra `web/index.html`.

## Versao standalone

Arquivo unico portatil:

```text
web/dist/index.html
```
