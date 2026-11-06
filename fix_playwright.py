import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_fix_playwright_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Localiza a rota do PDF consolidado
padrao = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)

match = padrao.search(main_code)
if not match:
    print("[ERRO] Rota não encontrada.")
    exit()

bloco_antigo = match.group(0)

# Substitui apenas o "async def" por "def" e corrige o retorno (await desnecessário)
novo_bloco = bloco_antigo.replace(
    '@app.get("/gerar_pdf_relatorio_consolidado/{id}")\nasync def gerar_pdf_relatorio_consolidado(id: int):',
    '@app.get("/gerar_pdf_relatorio_consolidado/{id}")\ndef gerar_pdf_relatorio_consolidado(id: int):'
)

main_code = main_code.replace(bloco_antigo, novo_bloco)

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Rota corrigida: 'async def' removido (agora é 'def').")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Gerar PDF novamente.")
