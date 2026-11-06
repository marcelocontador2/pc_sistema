import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c
    removidos = 0

    # Encontra todos os blocos <script>...</script> que contenham "ORDENACAO" ou "ordem" e "setTimeout"
    padrao_script = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    
    matches = list(padrao_script.finditer(c))
    for m in reversed(matches):
        bloco = m.group(1)
        # Verifica se o bloco e o de ordenacao (contem "setTimeout" e "ordem" ou "ORDENACAO")
        if 'setTimeout' in bloco and ('ORDENACAO' in bloco or 'ordem' in bloco or 'submenu.appendChild' in bloco):
            c = c[:m.start()] + c[m.end():]
            removidos += 1
            print(f"[OK] {arq} - Bloco de script de ordenacao removido (posicao {m.start()}).")

    if removidos > 0:
        shutil.copy2(arq, f"{arq}.bak_remove_ordenacao_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - {removidos} bloco(s) de ordenacao removido(s).")
    else:
        print(f"[AVISO] {arq} - Nenhum bloco de ordenacao encontrado.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
