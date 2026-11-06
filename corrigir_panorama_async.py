import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_fix_async_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1) Adiciona 'async' nas funcoes que usam 'await'
html = html.replace("function carregarPanorama() {", "async function carregarPanorama() {")
html = html.replace("function salvarPanorama() {", "async function salvarPanorama() {")

# 2) Conserta o botao "Gerar PDF" (que estava sem onclick)
html = re.sub(
    r'<button class="btn btn-pdf"\s*>',
    '<button class="btn btn-pdf" onclick="gerarPDFPanorama()">',
    html
)

# 3) Conserta o botao "Verificar" (que nao tinha onclick)
# Procura o botao que contem o texto "Verificar" e adiciona o onclick
def add_onclick_verificar(match):
    tag = match.group(0)
    if 'onclick=' not in tag:
        return tag.replace('<button', '<button onclick="carregarPanorama()"')
    return tag

html = re.sub(r'<button[^>]*>\s*Verificar\s*</button>', add_onclick_verificar, html, flags=re.IGNORECASE)

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Funcoes marcadas como 'async'.")
print("[OK] Botao 'Verificar' mapeado para carregarPanorama().")
print("[OK] Botao 'Gerar PDF' mapeado para gerarPDFPanorama().")
print("\n=== PROXIMO PASSO ===")
print("1. O servidor NAO precisa ser reiniciado.")
print("2. Va no navegador: http://127.0.0.1:9994/panorama")
print("3. Aperte Ctrl + Shift + R (MUITO IMPORTANTE para limpar o cache).")
print("4. Clique nos botoes. Agora eles devem funcionar!")
