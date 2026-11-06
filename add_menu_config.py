import glob, os, shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
alterados = 0

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    if not os.path.exists(arq):
        continue
    c = open(arq, encoding="utf-8", errors="ignore").read()
    if 'href="/configuracoes"' in c:
        print(f"[AVISO] {arq} ja tem link para configuracoes.")
        continue

    idx = c.find('href="/base_legal"')
    if idx == -1:
        idx = c.find('href="/importar"')
    if idx != -1:
        end_li = c.find('</li>', idx)
        if end_li != -1:
            novo_li = '\n    <li><a href="/configuracoes" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Configuracoes</a></li>'
            c = c[:end_li+5] + novo_li + c[end_li+5:]
            shutil.copy2(arq, f"{arq}.bak_config_{ts}")
            open(arq, "w", encoding="utf-8").write(c)
            alterados += 1
            print(f"[OK] {arq} - link Configuracoes adicionado.")

print(f"\n[OK] {alterados} arquivos alterados.")
