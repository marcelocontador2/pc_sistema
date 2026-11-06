import requests, sqlite3, os

db_path = os.path.join("pc_storage", "banco_dados.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def buscar_id(tabela, periodo="2026-TRIMESTRE-3"):
    try:
        cursor.execute(f"SELECT id FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
        r = cursor.fetchone()
        return r[0] if r else None
    except:
        return None

# Mapeamento correto
testes = [
    ("analise_bp", "historico_analise_bp", "/gerar_pdf_analise_bp/{id}"),
    ("analise_dfc", "historico_analise_dfc", "/gerar_pdf_analise_dfc/{id}"),
    ("analise_orcamentaria", "historico_analise_orcamentaria", "/gerar_pdf_analise_orcamentaria/{id}"),
    ("analise_financeira_bf", "historico_analise_financeira_bf", "/gerar_pdf_analise_financeira_bf/{id}"),
    ("analise_patrimonial", "historico_analise_patrimonial", "/gerar_pdf_analise_patrimonial/{id}"),
    ("liquidez", "historico_liquidez", "/gerar_pdf_liquidez/{id}"),
    ("panorama", "historico_panorama", "/gerar_pdf_panorama/{id}"),
    ("centro_custos", "historico_centro_custos", "/gerar_pdf_centro_custos/{id}"),
    ("integridade", "historico_integridade_matriz", "/gerar_pdf_integridade_matriz/{id}"),
]

print("=== TESTANDO ROTAS DE PDF INDIVIDUAIS ===\n")
for nome, tabela, rota in testes:
    hid = buscar_id(tabela)
    if not hid:
        print(f"✗ {nome}: SEM histórico para o período")
        continue
    url = f"http://127.0.0.1:9994{rota.replace('{id}', str(hid))}"
    try:
        r = requests.get(url, timeout=15)
        print(f"{'✓' if r.status_code == 200 else '✗'} {nome} (id={hid}): {r.status_code}")
    except Exception as e:
        print(f"✗ {nome}: {e}")

# Comparativos (sem ID, por período)
print("\n=== COMPARATIVOS ===")
for nome, rota in [
    ("comparativo_receitas", "/gerar_pdf_comparativo_receitas?periodo=2026-TRIMESTRE-3"),
    ("comparativo_despesas", "/gerar_pdf_comparativo_despesas?periodo=2026-TRIMESTRE-3"),
    ("custo_pessoal", "/gerar_pdf_custo_pessoal?id=" + str(buscar_id("historico_custo_pessoal") or "")),
]:
    url = f"http://127.0.0.1:9994{rota}"
    try:
        r = requests.get(url, timeout=15)
        print(f"{'✓' if r.status_code == 200 else '✗'} {nome}: {r.status_code}")
    except Exception as e:
        print(f"✗ {nome}: {e}")

conn.close()
