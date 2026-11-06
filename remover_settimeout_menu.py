import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # Remove os scripts que adicionam itens fora de ordem (Custo de Pessoal, Centro de Custos, etc.)
    # Padrao: script que contem "submenuAnalises.appendChild(li)" e "setTimeout"
    # Vamos remover os blocos de script que contem "submenuAnalises.appendChild(li)"
    padrao = re.compile(
        r'<script>\s*document\.addEventListener\("DOMContentLoaded",\s*function\(\)\s*\{.*?submenuAnalises\.appendChild\(li\).*?\}\);\s*\}\);\s*</script>',
        re.DOTALL
    )
    c_novo = padrao.sub('', c)
    
    if c_novo != c:
        c = c_novo
        print(f"[OK] {arq} - Scripts que adicionavam itens fora de ordem removidos.")
    else:
        print(f"[AVISO] {arq} - Nenhum script de appendChild encontrado para remover.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_remove_settimeout_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
