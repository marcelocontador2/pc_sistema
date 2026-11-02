c = open('main.py', encoding='utf-8-sig').read()

if "def excluir_multiplos_custo_pessoal" not in c:
    nova_rota = r'''
@app.post("/excluir_multiplos_custo_pessoal")
async def excluir_multiplos_custo_pessoal(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids:
        return {"ok": False, "mensagem": "Nenhum ID fornecido."}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Monta a query com placeholders para evitar SQL Injection
    placeholders = ",".join(["?"] * len(ids))
    cursor.execute(f"DELETE FROM historico_custo_pessoal WHERE id IN ({placeholders})", ids)
    conn.commit()
    excluidos = cursor.rowcount
    conn.close()
    
    return {"ok": True, "excluidos": excluidos}
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota de exclusão múltipla adicionada ao main.py!")
else:
    print("[AVISO] A rota de exclusão múltipla já existe.")
