import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")

print("=" * 60)
print("AUDITORIA COMPLETA DO FRONTEND")
print("=" * 60)

# 1. O que esta no HTML (arquivo em disco)
html = Path("pc_frontend/relatorio_consolidado.html").read_text(encoding="utf-8")
print(f"\n[1] Arquivo HTML em disco:")
print(f"    Tamanho: {len(html)} caracteres")
print(f"    Contem 'function marcarTodos': {'function marcarTodos' in html}")
print(f"    Contem 'function excluirSelecionados': {'function excluirSelecionados' in html}")
print(f"    Contem 'chk-historico': {'chk-historico' in html}")
print(f"    Contem 'btn-excluir-todos': {'btn-excluir-todos' in html}")
print(f"    Contem 'selecionar-todos': {'selecionar-todos' in html}")

# 2. O que a API esta entregando (HTTP GET)
print(f"\n[2] O que a API entrega na rota /relatorio_consolidado:")
try:
    from pc_backend.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    r = client.get('/relatorio_consolidado')
    conteudo = r.text
    print(f"    Status HTTP: {r.status_code}")
    print(f"    Tamanho: {len(conteudo)} caracteres")
    print(f"    Contem 'function marcarTodos': {'function marcarTodos' in conteudo}")
    print(f"    Contem 'function excluirSelecionados': {'function excluirSelecionados' in conteudo}")
    print(f"    Contem 'chk-historico': {'chk-historico' in conteudo}")
    print(f"    Contem 'btn-excluir-todos': {'btn-excluir-todos' in conteudo}")
    print(f"    Contem 'selecionar-todos': {'selecionar-todos' in conteudo}")
    
    # Se a API entrega algo diferente do arquivo, mostra onde diverge
    if conteudo != html:
        print("\n    [AVISO] O conteudo da API e DIFERENTE do arquivo em disco!")
        print("    Possiveis causas: cache do FastAPI ou caminho diferente.")
    else:
        print("\n    [OK] O conteudo da API e IDENTICO ao arquivo em disco.")
except Exception as e:
    print(f"    [ERRO] {e}")

# 3. O que esta no banco (historico salvo)
print(f"\n[3] Registros no banco (historico_relatorio_consolidado):")
try:
    import psycopg2
    from pc_backend.app.config import PG_CONFIG
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo FROM historico_relatorio_consolidado ORDER BY id DESC")
    rows = cur.fetchall()
    print(f"    Total de registros: {len(rows)}")
    for r in rows[:5]:
        print(f"    id={r[0]}, periodo={r[1]}")
    conn.close()
except Exception as e:
    print(f"    [ERRO] {e}")

# 4. O que a rota de historico retorna
print(f"\n[4] O que a API entrega na rota /historico_relatorio_consolidado:")
try:
    r = client.get('/historico_relatorio_consolidado')
    dados = r.json()
    print(f"    Status HTTP: {r.status_code}")
    print(f"    Total de itens: {len(dados)}")
    for d in dados[:3]:
        print(f"    id={d.get('id')}, periodo={d.get('periodo')}")
except Exception as e:
    print(f"    [ERRO] {e}")

# 5. O que a rota de exclusao retorna
print(f"\n[5] Teste da rota /excluir_multiplos_relatorio_consolidado (ID 999999):")
try:
    r = client.post('/excluir_multiplos_relatorio_consolidado', json={'ids': [999999]})
    print(f"    Status HTTP: {r.status_code}")
    print(f"    Resposta: {r.text}")
except Exception as e:
    print(f"    [ERRO] {e}")

print("\n" + "=" * 60)
print("FIM DA AUDITORIA")
print("=" * 60)
