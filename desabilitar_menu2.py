import glob, os, re, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pasta = "pc_frontend"
alterados = 0

# Regex: encontra o <a ... id="menu-demonstracoes" ...>...</a>
padrao = re.compile(
    r'<a\s+([^>]*?)id="menu-demonstracoes"([^>]*)>([^<]*)</a>',
    re.IGNORECASE
)

for arq in glob.glob(os.path.join(pasta, "*.html")):
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    if 'id="menu-demonstracoes"' not in c:
        continue

    c_backup = c

    def substituir(match):
        antes = match.group(1) or ""
        depois = match.group(2) or ""
        texto = match.group(3) or ""
        # Remove onclick e class="active", adiciona estilo de desabilitado
        antes_limpo = re.sub(r'onclick="[^"]*"\s*', '', antes)
        depois_limpo = re.sub(r'onclick="[^"]*"\s*', '', depois)
        depois_limpo = depois_limpo.replace('class="active"', 'class="disabled"')
        # Monta tag nova
        return f'<a {antes_limpo}id="menu-demonstracoes" {depois_limpo} style="pointer-events: none; opacity: 0.5; cursor: default; display: block; padding: 10px 0px; text-decoration: none; color: #333; font-weight: bold;" aria-disabled="true" title="Em desenvolvimento">{texto}</a>'

    c_novo = padrao.sub(substituir, c)

    if c_novo != c_backup:
        bak = f"{arq}.bak_menu_{ts}"
        shutil.copy2(arq, bak)
        open(arq, "w", encoding="utf-8").write(c_novo)
        alterados += 1
        print(f"[OK] {arq} - menu desabilitado")

print(f"\n[OK] {alterados} arquivos alterados.")

# Mostra como ficou o index.html
if alterados > 0:
    print("\n--- Trecho do index.html apos alteracao ---")
    c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()
    idx = c.find('id="menu-demonstracoes"')
    if idx != -1:
        print(repr(c[max(0, idx-50):idx+200]))
