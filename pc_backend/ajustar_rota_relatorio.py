import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra a rota api_relatorio_centro_custos e substitui a lógica de processamento
padrao = r'def api_relatorio_centro_custos\(.*?return \{.*?\}'

nova_rota = '''def api_relatorio_centro_custos(periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = "2026-TRIMESTRE-2"):
    import sqlite3, os, json
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    def buscar_dados(periodo):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None  # Retorna None se não encontrar
    
    dados_atual = buscar_dados(periodo_atual)
    dados_anterior = buscar_dados(periodo_anterior)
    conn.close()
    
    def processar(dados):
        if not dados:
            return {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0}
        centros = dados.get("centros", [])
        centros = [c for c in centros if c.get("nome") != "Centro de Custo"]
        total = sum(c.get("valor", 0) for c in centros)
        return {
            "total": total,
            "centros": centros,
            "maior_centro": max(centros, key=lambda x: x.get("valor", 0)) if centros else {"nome": "-", "valor": 0},
            "media_mensal": total / 6 if total > 0 else 0,
        }
    
    atual = processar(dados_atual)
    anterior = processar(dados_anterior) if dados_anterior else None
    
    # Se não houver dados anteriores, retorna apenas o atual com flag
    if anterior is None:
        return {
            "periodo_atual": periodo_atual,
            "periodo_anterior": None,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0},
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
    c = re.sub(padrao, nova_rota, c, flags=re.DOTALL)
    print("[OK] Rota de relatório atualizada com tratamento de período anterior!")
else:
    print("[AVISO] Rota não encontrada.")

open('main.py', 'w', encoding='utf-8').write(c)
