import glob, os, re, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pasta = "pc_frontend"
alterados = 0

# Regex mais flexivel: qualquer <a ... id="menu-demonstracoes" ...>...</a>
# Aceita quebra de linha no texto e atributos em qualquer ordem
padrao = re.compile(
    r'<a\s+([^>]*?id="menu-demonstracoes"[^>]*?)>([\s\S]*?)</a>',
    re.IGNORECASE
)

for arq in glob.glob(os.path.join(pasta, "*.html")):
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    if 'id="menu-demonstracoes"' not in c:
        continue

    # Pula se ja foi desabilitado (tem pointer-events: none e class="disabled")
    if 'id="menu-demonstracoes"' in c and 'pointer-events: none' in c and 'class="disabled"' in c:
        # Mas pode ter mais de um; so pula se TODOS os blocos ja estao corretos
        pass

    c_backup = c

    def substituir(match):
        atributos = match.group(1) or ""
        texto = match.group(2) or ""
        # Remove onclick, class e style antigos
        atributos_limpos = re.sub(r'onclick="[^"]*"\s*', '', atributos)
        atributos_limpos = re.sub(r'class="[^"]*"\s*', '', atributos_limpos)
        atributos_limpos = re.sub(r'style="[^"]*"\s*', '', atributos_limpos)
        # Monta tag nova com id, class disabled e style
        return (
            f'<a id="menu-demonstracoes" class="disabled" '
            f'{atributos_limpos}'
            f'style="pointer-events: none; opacity: 0.5; cursor: default; '
            f'display: block; padding: 10px 0px; text-decoration: none; '
            f'color: #333; font-weight: bold;" '
            f'aria-disabled="true" title="Em desenvolvimento">{texto}</a>'
        )

    c_novo = padrao.sub(substituir, c)

    if c_novo != c_backup:
        bak = f"{arq}.bak_menu2_{ts}"
        shutil.copy2(arq, bak)
        open(arq, "w", encoding="utf-8").write(c_novo)
        alterados += 1
        # Conta quantas ocorrencias
        n = len(padrao.findall(c_backup))
        print(f"[OK] {arq} - {n} menu(s) desabilitado(s)")

print(f"\n[OK] {alterados} arquivos alterados.")
