c = open('main.py', encoding='utf-8-sig').read()

# Verifica se a rota já existe para não duplicar
if "def api_relatorio_centro_custos" not in c:
    nova_rota = r'''
@app.get("/api/relatorio_centro_custos")
def api_relatorio_centro_custos(periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = "2026-TRIMESTRE-2"):
    import sqlite3, os, json
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def buscar_dados(periodo):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return {"centros": []}
    
    dados_atual = buscar_dados(periodo_atual)
    dados_anterior = buscar_dados(periodo_anterior)
    conn.close()
    
    def processar(dados):
        centros = dados.get("centros", [])
        # Ignora o cabeçalho repetido
        centros = [c for c in centros if c.get("nome") != "Centro de Custo"]
        
        total = sum(c.get("valor", 0) for c in centros)
        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / 6 if total > 0 else 0,
        }
    
    atual = processar(dados_atual)
    anterior = processar(dados_anterior)
    
    return {
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', nova_rota + '\nif __name__ == "__main__":')
    else:
        c += "\n" + nova_rota
    
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rota de relatório criada no backend!")
else:
    print("[AVISO] Rota já existe.")
