import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c
    removidos = 0

    # Estrategia: encontrar todos os blocos <script>...</script> que contenham "submenuAnalises.appendChild"
    # e remover o bloco inteiro.
    padrao_script = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    
    # Itera sobre os blocos de script (de tras para frente, para nao bagunçar os indices)
    matches = list(padrao_script.finditer(c))
    for m in reversed(matches):
        bloco = m.group(1)
        # Verifica se o bloco contem "submenuAnalises.appendChild" E "setTimeout"
        if 'submenuAnalises.appendChild' in bloco and 'setTimeout' in bloco:
            # Remove o bloco inteiro
            c = c[:m.start()] + c[m.end():]
            removidos += 1
            print(f"[OK] {arq} - Bloco de script removido (posicao {m.start()}).")

    if removidos > 0:
        shutil.copy2(arq, f"{arq}.bak_remove_timeout2_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - {removidos} bloco(s) de script removido(s).")
    else:
        print(f"[AVISO] {arq} - Nenhum bloco de script com 'submenuAnalises.appendChild' e 'setTimeout' encontrado.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
