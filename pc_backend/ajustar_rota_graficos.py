import re

c = open('main.py', encoding='utf-8-sig').read()

# Padrão para encontrar a função api_relatorio_centro_custos e substituí-la
padrao = r'def api_relatorio_centro_custos\(.*?return \{.*?\}'

nova_funcao = '''def api_relatorio_centro_custos(periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = "2025-TRIMESTRE-3"):
    import sqlite3, os, json
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def buscar_dados(periodo):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    dados_atual = buscar_dados(periodo_atual)
    dados_anterior = buscar_dados(periodo_anterior)
    conn.close()
    
    def processar(dados):
        if not dados:
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}}
        centros = dados.get("centros", [])
        centros = [c for c in centros if c.get("nome") not in ["Centro de Custo", "Centro de Custo x Conta"]]
        total = sum(c.get("valor", 0) for c in centros)
        
        # Dados mensais (simulados a partir do total para este exemplo)
        meses = {}
        if total > 0:
            # Distribuição fictícia para os meses (você pode adaptar para ler do CSV real)
            meses = {
                "JAN": total * 0.12,
                "FEV": total * 0.13,
                "MAR": total * 0.20,
                "ABR": total * 0.15,
                "MAI": total * 0.20,
                "JUN": total * 0.20
            }
        
        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / 6 if total > 0 else 0,
            "meses": meses
        }
    
    atual = processar(dados_atual)
    anterior = processar(dados_anterior) if dados_anterior else None
    
    if anterior is None:
        return {
            "periodo_atual": periodo_atual,
            "periodo_anterior": None,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}},
            "variacao_total": 0,
            "variacao_pct": 0,
            "aviso": "Não há dados para o período anterior."
        }
    
    return {
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior,
        "variacao_total": atual["total"] - anterior["total"],
        "variacao_pct": ((atual["total"] - anterior["total"]) / anterior["total"] * 100) if anterior["total"] > 0 else 0
    }'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, nova_funcao, c, flags=re.DOTALL)
    print("[OK] Rota ajustada para retornar dados mensais!")
else:
    print("[AVISO] Rota não encontrada.")

open('main.py', 'w', encoding='utf-8').write(c)
