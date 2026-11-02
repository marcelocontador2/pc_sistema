import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra a função api_relatorio_centro_custos e adiciona o parâmetro id
padrao = r'def api_relatorio_centro_custos\(periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = "2025-TRIMESTRE-3"\):'
novo = 'def api_relatorio_centro_custos(id: int = None, periodo_atual: str = "2026-TRIMESTRE-3", periodo_anterior: str = "2025-TRIMESTRE-3"):'

if re.search(padrao, c):
    c = re.sub(padrao, novo, c)
    print("[OK] Função api_relatorio_centro_custos ajustada para aceitar ID!")

# Dentro da função, adiciona lógica para buscar por ID
trecho_antigo = '''    def buscar_dados(periodo):
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None'''

trecho_novo = '''    def buscar_dados(periodo=None, id_historico=None):
        if id_historico:
            cur.execute("SELECT dados_json FROM historico_centro_custos WHERE id = ?", (id_historico,))
        else:
            cur.execute("SELECT dados_json FROM historico_centro_custos WHERE periodo = ? ORDER BY id DESC LIMIT 1", (periodo,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return None'''

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Lógica de buscar_dados ajustada para aceitar ID!")

# Ajusta as chamadas para passar o ID (se aplicável)
c = c.replace(
    'dados_atual = buscar_dados(periodo_atual)',
    'dados_atual = buscar_dados(periodo_atual, id)'
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py ajustado para buscar por ID!")
