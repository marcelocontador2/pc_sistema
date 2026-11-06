import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # Remove os scripts que adicionam itens via setTimeout
    padrao = re.compile(
        r'<script>\s*document\.addEventListener\("DOMContentLoaded",\s*function\(\)\s*\{.*?setTimeout.*?submenuAnalises\.appendChild\(li\).*?\}\);\s*\}\);\s*</script>',
        re.DOTALL
    )
    c = padrao.sub('', c)

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_remove_timeout_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Scripts setTimeout removidos.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
