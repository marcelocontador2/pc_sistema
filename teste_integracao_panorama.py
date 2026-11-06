import requests, json

base_url = "http://127.0.0.1:9994"
periodo = "2026-TRIMESTRE-3"

print("=== 1. TESTANDO O CÁLCULO (GET /api/panorama) ===")
res_calc = requests.get(f"{base_url}/api/panorama/{periodo}")
print(f"Status: {res_calc.status_code}")
dados = res_calc.json()
print(json.dumps(dados, indent=2, ensure_ascii=False))

print("\n=== 2. TESTANDO O SALVAMENTO (POST /salvar_panorama) ===")
res_save = requests.post(f"{base_url}/salvar_panorama/{periodo}")
print(f"Status: {res_save.status_code}")
print(res_save.json())

print("\n=== 3. TESTANDO A BUSCA DO HISTÓRICO (GET /historico_panorama) ===")
res_hist = requests.get(f"{base_url}/historico_panorama")
print(f"Status: {res_hist.status_code}")
historico = res_hist.json()
print(f"Históricos encontrados: {len(historico)}")

if len(historico) > 0:
    id_salvo = historico[0]['id']
    print(f"\n=== 4. TESTANDO O BOTÃO EXIBIR (GET /historico_panorama/{id_salvo}) ===")
    res_exibir = requests.get(f"{base_url}/historico_panorama/{id_salvo}")
    print(f"Status: {res_exibir.status_code}")
    print(json.dumps(res_exibir.json(), indent=2, ensure_ascii=False))
else:
    print("[ERRO] Nenhum histórico foi salvo!")
