import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_trim_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# A busca exata atual
old_logic = 'cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))'

# Nova busca que ignora espaços em branco e diferenças de maiúsculas/minúsculas
new_logic = 'cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE TRIM(UPPER(periodo)) = TRIM(UPPER(?)) ORDER BY id DESC LIMIT 1", (periodo,))'

if old_logic in main_code:
    main_code = main_code.replace(old_logic, new_logic)
    print("[OK] Busca ajustada para ignorar espaços (TRIM) e maiúsculas/minúsculas (UPPER).")
else:
    print("[AVISO] Não encontrei a linha de busca exata no main.py.")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Verificar Dados novamente.")
