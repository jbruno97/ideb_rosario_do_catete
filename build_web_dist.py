from pathlib import Path
import base64
root = Path('web')
html = (root / 'index.html').read_text(encoding='utf-8-sig')
css = (root / 'css' / 'presentation.css').read_text(encoding='utf-8-sig')
scripts = []
for name in ['data.js','storytelling.js','charts.js','navigation.js','presentation.js']:
    scripts.append((root / 'js' / name).read_text(encoding='utf-8-sig'))
html = html.replace('<link rel="stylesheet" href="css/presentation.css">', f'<style>\n{css}\n</style>')
html = html.replace('<script src="js/data.js"></script><script src="js/storytelling.js"></script><script src="js/charts.js"></script><script src="js/navigation.js"></script><script src="js/presentation.js"></script>', '<script>\n' + '\n'.join(scripts) + '\n</script>')
logo = root / 'assets' / 'img' / 'logo_semed.png'
if logo.exists():
    data_uri = 'data:image/png;base64,' + base64.b64encode(logo.read_bytes()).decode('ascii')
    html = html.replace('src="assets/img/logo_semed.png"', f'src="{data_uri}"')
(root / 'dist').mkdir(parents=True, exist_ok=True)
(root / 'dist' / 'index.html').write_text(html, encoding='utf-8')
print(root / 'dist' / 'index.html')
