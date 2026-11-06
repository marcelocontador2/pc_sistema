import shutil, datetime, re

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_pdf_comp_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Corrige o redirecionamento do COMPARATIVO_DESPESAS para a rota de PDF
c = c.replace(
    "window.open('/analise_comparativo_despesas', '_blank');",
    "window.open('/gerar_pdf_comparativo_despesas', '_blank');"
)

# 2. Verifica se a substituição foi aplicada
if '/gerar_pdf_comparativo_despesas' in c:
    print("[OK] Redirecionamento corrigido para /gerar_pdf_comparativo_despesas")
else:
    print("[AVISO] Substituição não aplicada. Tentando variação...")
    # Tenta substituir qualquer referência à tela por PDF
    c = c.replace(
        "'/analise_comparativo_despesas'",
        "'/gerar_pdf_comparativo_despesas'"
    )
    print("[OK] Substituição via variação aplicada")

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] index.html salvo")
