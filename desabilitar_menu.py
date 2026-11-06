import glob, os, re, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pasta = "pc_frontend"
alterados = 0
total_links = 0

# Regex para encontrar o link do menu
# Pode ser <a href="/demonstracoes">...</a> ou <a href="demonstracoes.html">...</a>
padrao = re.compile(
    r'<a\s+([^>]*?)href="(/demonstracoes|demonstracoes\.html)"([^>]*)>(.*?)</a>',
    re.IGNORECASE | re.DOTALL
)

for arq in glob.glob(os.path.join(pasta, "*.html")):
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    if "Demonstra" not in c:
        continue

    # Verifica se tem o link para /demonstracoes
    if '/demonstracoes' not in c and 'demonstracoes.html' not in c:
        continue

    c_backup = c

    def substituir(match):
        global total_links
        total_links += 1
        antes = match.group(1) or ""
        href = match.group(2)
        depois = match.group(3) or ""
        texto = match.group(4)
        # Monta o <a> desabilitado
        return f'<a {antes}href="#" {depois} style="pointer-events: none; opacity: 0.5; cursor: default;" aria-disabled="true" tabindex="-1" title="Em desenvolvimento">{texto}</a>'

    c_novo = padrao.sub(substituir, c)

    if c_novo != c_backup:
        # Faz backup
        bak = f"{arq}.bak_menu_{ts}"
        shutil.copy2(arq, bak)
        open(arq, "w", encoding="utf-8").write(c_novo)
        alterados += 1
        print(f"[OK] {arq} - desabilitado")

print(f"\n[OK] {alterados} arquivos alterados, {total_links} links desabilitados.")
