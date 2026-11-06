import sqlite3, json, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Pega o último histórico consolidado
cursor.execute("SELECT id, resultado_json FROM historico_relatorio_consolidado ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()

if row:
    id_cons, res_json = row
    print(f"Histórico consolidado ID: {id_cons}")
    dados = json.loads(res_json)
    modulos = dados.get("dados", {})
    
    print(f"\nMódulos disponíveis: {list(modulos.keys())}\n")
    
    # Mostra especificamente a estrutura do analise_bp
    if "analise_bp" in modulos:
        bp = modulos["analise_bp"]
        print("=== CONTEÚDO DE 'analise_bp' ===")
        print(f"Tipo: {type(bp)}")
        print(f"Chaves: {list(bp.keys()) if isinstance(bp, dict) else 'não é dict'}")
        print(f"Conteúdo (primeiros 1000 chars):")
        print(json.dumps(bp, indent=2, ensure_ascii=False)[:1000])
    else:
        print("[ERRO] 'analise_bp' NÃO está no JSON do consolidado!")
        
        # Verifica se está em outra chave
        for chave in modulos:
            if "bp" in chave.lower() or "balanco" in chave.lower():
                print(f"Possível correspondência: '{chave}'")
else:
    print("[ERRO] Nenhum histórico consolidado encontrado.")

conn.close()
