import re, shutil, datetime

arquivo = r"pc_backend\main.py"
backup = f"pc_backend\\main_backup_salvar_deadlock_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    codigo = f.read()

# Encontra a rota salvar_panorama e substitui pela versão sem deadlock
padrao = re.compile(r'@app\.post\("/salvar_panorama/\{periodo\}"\).*?(?=\n@app\.|\Z)', re.DOTALL)

if padrao.search(codigo):
    nova_rota = '''@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str):
    import sqlite3, json, os, datetime
    try:
        # Chama a funcao python DIRETAMENTE (sem fazer requisicao HTTP pra si mesmo)
        dados = await api_panorama(periodo)
        
        if dados.get("erro"):
            return {"erro": True, "mensagem": dados.get("mensagem", "Erro no calculo do panorama")}
            
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_panorama (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_panorama (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    codigo = padrao.sub(nova_rota, codigo)
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(codigo)
    print("[OK] Rota /salvar_panorama/ corrigida (Deadlock resolvido)!")
else:
    print("[AVISO] Nao achei a rota salvar_panorama.")

print("\n==============================================")
print("=== AÇÃO OBRIGATÓRIA: REINICIAR O SERVIDOR ===")
print("==============================================")
print("1. No terminal do uvicorn, aperte Ctrl+C.")
print("2. Suba de novo: cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. Va no navegador: http://127.0.0.1:9994/panorama")
print("4. Aperte Ctrl+Shift+R.")
print("5. Clique em Verificar, depois Salvar. E depois Exibir no item novo do historico.")
