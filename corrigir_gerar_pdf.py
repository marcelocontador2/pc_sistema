import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. Corrige a funcao gerarPDF no analise_bp.html
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_gerar_pdf_{ts}")
c = open(arq, encoding="utf-8", errors="ignore").read()

# Procura a funcao gerarPDF atual
idx = c.find("function gerarPDF()")
if idx != -1:
    # Encontra o final da funcao (proximo "}" no nivel correto)
    # Como a funcao esta incompleta, vamos substituir tudo ate o proximo "function" ou "</script>"
    fim = c.find("\n        function ", idx + 10)
    if fim == -1:
        fim = c.find("\n    </script>", idx)
    if fim == -1:
        fim = idx + 500

    # Nova funcao completa
    nova_funcao = '''function gerarPDF() {
        var sel = document.querySelector(".check-hist:checked");
        if (!sel) { alert("Selecione um item no historico."); return; }
        window.open('/gerar_pdf_analise_bp/' + sel.value, '_blank');
    }'''

    c = c[:idx] + nova_funcao + c[fim:]
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao gerarPDF corrigida (agora chama a rota /gerar_pdf_analise_bp/).")
else:
    print("[ERRO] Funcao gerarPDF nao encontrada.")
