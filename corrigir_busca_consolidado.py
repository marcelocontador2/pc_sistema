import re, shutil, datetime

# 1. CORRIGIR O TEXTO NA TELA (FRONTEND)
arq_html = r"pc_frontend\relatorio_consolidado.html"
shutil.copy2(arq_html, f"{arq_html}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Corrige o texto que estava mostrando o código JS na tela
html = html.replace(
    '<h4 style="margin-top: 15px; color: #dc3545;">✗ Faltando (${data.faltando.length}):</h4>',
    '<h4 style="margin-top: 15px; color: #dc3545;">✗ Faltando:</h4>'
)

with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Texto da tela corrigido.")

# 2. CORRIGIR A BUSCA NO BANCO (BACKEND)
arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_busca_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Vamos trocar a forma como o LIKE é montado. Em vez de buscar a string inteira, vamos buscar o ano e o trimestre de forma flexível.
old_like = 'cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))'

# A nova busca vai separar o ano e o trimestre da string "2026-TRIMESTRE-3"
new_logic = '''
            # Extrai ano e trimestre/mês do período selecionado
            partes = periodo.split("-")
            ano = partes[0] if len(partes) > 0 else ""
            tipo = partes[1] if len(partes) > 1 else ""
            valor = partes[2] if len(partes) > 2 else ""
            
            # Busca flexível (ex: %2026%3% ou %2026%TRIMESTRE-3%)
            termo_busca = f"%{ano}%"
            
            # Tenta achar registros que contenham o ano e o valor (ex: 3)
            cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE (periodo LIKE ? AND periodo LIKE ?) ORDER BY id DESC LIMIT 1", (termo_busca, f"%{valor}%"))
'''

if old_like in main_code:
    main_code = main_code.replace(old_like, new_logic)
    print("[OK] Lógica de busca no banco flexibilizada (ano + trimestre).")
else:
    print("[AVISO] Não encontrei a linha exata de busca no main.py.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Verificar Dados novamente.")
