import sys
import json
import psycopg2
from fastapi.testclient import TestClient
from pc_backend.main import app
from pc_backend.app.config import PG_CONFIG

sys.stdout.reconfigure(encoding="utf-8")

print("1. Buscando dados novos da API...")
client = TestClient(app)
r = client.get('/api/relatorio_consolidado/2026-TRIMESTRE-3')
dados_api = r.json()
print(f"   Modulos encontrados: {len(dados_api.get('encontrados', []))}")

if len(dados_api.get('encontrados', [])) < 14:
    print("[ERRO] A API ainda nao esta retornando os 14 modulos. Abortando.")
    sys.exit(1)

print("2. Conectando ao banco...")
conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()

# Pega o ultimo ID salvo
cur.execute("SELECT id FROM historico_relatorio_consolidado ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
if not row:
    print("[ERRO] Nenhum historico no banco. Abortando.")
    sys.exit(1)

ultimo_id = row[0]
print(f"   Ultimo ID no banco: {ultimo_id}")

# Prepara o JSON no mesmo formato que o PDF espera
dados_para_salvar = {
    "periodo": "2026-TRIMESTRE-3",
    "data_geracao": "2026-11-18 18:55:12",
    "dados": dados_api.get("encontrados", [])
}

json_str = json.dumps(dados_para_salvar, ensure_ascii=False)

print("3. Atualizando o banco com os dados novos...")
cur.execute(
    "UPDATE historico_relatorio_consolidado SET resultado_json = %s WHERE id = %s",
    (json_str, ultimo_id)
)
conn.commit()
print(f"   [OK] ID {ultimo_id} atualizado com {len(dados_api.get('encontrados', []))} modulos.")

# Verifica se salvou certo
cur.execute("SELECT resultado_json FROM historico_relatorio_consolidado WHERE id = %s", (ultimo_id,))
row = cur.fetchone()
if row:
    dados_salvos = json.loads(row[0])
    print(f"   Verificacao: {len(dados_salvos.get('dados', []))} modulos no banco.")
    for item in dados_salvos.get('dados', []):
        nome = item.get('nome', '?')
        tem_dados = 'dados' in item
        if 'DFC' in nome or 'Liquidez' in nome:
            print(f"   -> {nome}: tem dados? {tem_dados}")

conn.close()
print("[OK] Banco atualizado. Agora gere o PDF pelo navegador.")
