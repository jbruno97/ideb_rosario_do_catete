# Publicação no GitHub Pages

O arquivo publicado deve ser `docs/index.html`. Ele é uma versão standalone da apresentação selecionada com 6 slides, com CSS, JavaScript, dados e logo embutidos.

## Opção recomendada: publicar pela pasta docs

1. Crie um repositório no GitHub.
2. No terminal, dentro desta pasta `ideb_rosario_catete`, rode:

```powershell
git init
git add .
git commit -m "Publica apresentação IDEB Rosário do Catete"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

3. No GitHub, abra o repositório e vá em:

`Settings > Pages > Build and deployment`

4. Configure:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`

5. Salve. O GitHub vai publicar a apresentação pelo arquivo `docs/index.html`.

## Arquivos principais

- `docs/index.html`: arquivo final para publicação.
- `docs/.nojekyll`: evita processamento pelo Jekyll.
- `web/apresentacao_selecionada.html`: cópia de trabalho da apresentação de 6 slides.
- `web/index.html`: apresentação completa original preservada.
