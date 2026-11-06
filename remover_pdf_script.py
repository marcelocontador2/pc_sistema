import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/liquidez.html"
shutil.copy2(arq, f"{arq}.bak_remove_pdf_script_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Remove o bloco de script que adiciona o addEventListener ao btnPdf
# (o script que comeca com document.addEventListener('DOMContentLoaded', function() {
# e contem btnPdf.addEventListener('click', function(e) { ... });)
padrao = re.compile(
    r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\',\s*function\(\)\s*\{.*?btnPdf\.addEventListener\(\'click\',\s*function\(e\)\s*\{.*?\}\);\s*\}\);\s*</script>',
    re.DOTALL
)

c_novo = padrao.sub('', c)

if c_novo != c:
    c = c_novo
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Bloco de script que adicionava addEventListener ao btnPdf removido.")
else:
    print("[AVISO] Bloco de script nao encontrado. Tentando variacao...")
    # Tenta remover qualquer script que contenha "btnPdf.addEventListener"
    padrao2 = re.compile(r'<script>.*?btnPdf\.addEventListener.*?</script>', re.DOTALL)
    c_novo2 = padrao2.sub('', c)
    if c_novo2 != c:
        c = c_novo2
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Bloco removido via regex2.")
    else:
        print("[ERRO] Nao foi possivel remover o bloco de script.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
