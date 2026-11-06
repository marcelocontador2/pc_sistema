import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_busca_exata_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# A lógica anterior (flexível) que estava quebrando
old_logic = '''
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

# Lógica correta (busca exata)
new_logic = '''
            # Busca exata pelo período (padrão do sistema)
            cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
'''

if old_logic in main_code:
    main_code = main_code.replace(old_logic, new_logic)
    print("[OK] Lógica de busca corrigida para EXATA (WHERE periodo = ?).")
else:
    # Tenta encontrar a versão que está no arquivo (pode ter pequenas diferenças de espaços)
    padrao = re.compile(r'# Extrai ano e trimestre.*?cursor\.execute\(f"SELECT.*?\)\n', re.DOTALL)
    if padrao.search(main_code):
        main_code = padrao.sub(new_logic.strip(), main_code)
        print("[OK] Lógica de busca corrigida via Regex.")
    else:
        print("[AVISO] Não encontrei o bloco exato da lógica antiga. Verificando...")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Verificar Dados novamente.")
