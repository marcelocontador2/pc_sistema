import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Verificar/Criar a rota de exclusão múltipla
if "def excluir_panorama_multiplos" not in codigo:
    print("[AUDITORIA] Rota de exclusão múltipla NAO encontrada. Injetando...")
    rota_exclusao = '''
@app.post("/excluir_panorama_multiplos")
async def excluir_panorama_multiplos(request: Request):
    import sqlite3, os
    try:
        dados = await request.json()
        ids = dados.get("ids", [])
        if not ids:
            return {"erro": True, "mensagem": "Nenhum ID enviado"}
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"DELETE FROM historico_panorama WHERE id IN ({placeholders})", ids)
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": f"{cursor.rowcount} itens excluídos"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    codigo += "\n" + rota_exclusao
    print("[AUDITORIA] Rota de exclusão múltipla injetada.")
else:
    print("[AUDITORIA] Rota de exclusão múltipla OK.")

# 2. Verificar/Criar a rota de cálculo (API)
if "def api_panorama(" not in codigo:
    print("[AUDITORIA] Funcao api_panorama NAO encontrada. Algo muito errado.")
else:
    print("[AUDITORIA] Funcao api_panorama OK.")

# 3. Salvar
with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)

print("\n=== PROXIMO PASSO ===")
print("1. PARE o servidor uvicorn (Ctrl+C).")
print("2. Suba o servidor NOVAMENTE (cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994).")
print("3. No navegador: Ctrl+Shift+R.")
print("4. Teste o botao Excluir Selecionado marcando mais de um item.")
print("5. Teste tambem o botao Verificar para ver se os valores voltam a aparecer.")
