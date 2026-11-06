import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Usando chr() para acentos (evita corrupcao no terminal)
A = chr(0xC1)  # Á
a = chr(0xE1)  # á
e = chr(0xE9)  # é
i = chr(0xED)  # í
o = chr(0xF3)  # ó
u = chr(0xFA)  # ú
c = chr(0xE7)  # ç
a_til = chr(0xE3)  # ã
o_til = chr(0xF5)  # õ

analise_bp = f"An{a}lise BP"

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # 1. Adiciona o link no HTML estatico (se nao existir)
    if 'href="/analise_bp"' not in c:
        # Procura o link do BF
        idx_bf = c.find('href="/analise_financeira_bf"')
        if idx_bf != -1:
            fim_bf = c.find('</a>', idx_bf) + 4
            if fim_bf != -1:
                link_bp = f'\n            <a href="/analise_bp" style="text-decoration:none; color:inherit;" class="menu-item">{analise_bp}</a>'
                c = c[:fim_bf] + link_bp + c[fim_bf:]
                print(f"[OK] {arq} - Link '{analise_bp}' adicionado.")

    # 2. Adiciona o item na lista linksParaMover (se nao existir)
    if f"'{analise_bp}'" not in c:
        padrao = re.compile(r"(const linksParaMover = \[)(.*?)(\];)", re.DOTALL)
        match = padrao.search(c)
        if match:
            lista_atual = match.group(2)
            lista_nova = lista_atual.rstrip() + f",\n        '{analise_bp}'"
            c = c[:match.start(2)] + lista_nova + c[match.end(2):]
            print(f"[OK] {arq} - '{analise_bp}' adicionada à lista linksParaMover.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_add_bp_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
