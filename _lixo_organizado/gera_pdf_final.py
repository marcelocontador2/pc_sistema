import sys
from fastapi.testclient import TestClient
from pc_backend.main import app

sys.stdout.reconfigure(encoding="utf-8")

print("Conectando a API...")
client = TestClient(app)

# 1. Gera o relatorio na API
print("Buscando dados do periodo 2026-TRIMESTRE-3...")
r = client.get('/api/relatorio_consolidado/2026-TRIMESTRE-3')
dados = r.json()
print(f"Status: {r.status_code}")
print(f"Modulos encontrados: {len(dados.get('encontrados', []))}")

if len(dados.get('encontrados', [])) < 14:
    print("[ERRO] A API nao esta retornando os 14 modulos. Abortando.")
    sys.exit(1)

# 2. Salva no historico (isso vai gerar um ID novo)
print("Salvando no historico para gerar o ID do PDF...")
r_salvar = client.post('/salvar_relatorio_consolidado/2026-TRIMESTRE-3')
print(f"Status do salvamento: {r_salvar.status_code}")

# 3. Pega o ID do ultimo relatorio salvo
r_hist = client.get('/historico_relatorio_consolidado')
historico = r_hist.json()
if historico:
    ultimo_id = historico[0]['id']
    print(f"ID do relatorio gerado: {ultimo_id}")
else:
    print("Erro: Nenhum historico encontrado apos salvar.")
    sys.exit(1)

# 4. Gera o PDF
print("Gerando PDF...")
r_pdf = client.get(f'/gerar_pdf_relatorio_consolidado/{ultimo_id}')

if r_pdf.status_code == 200:
    # Salva na area de trabalho
    caminho_saida = r"C:\Users\Marcelo Medeiros\Desktop\relatorio_CONSOLIDADO_CORRIGIDO.pdf"
    with open(caminho_saida, "wb") as f:
        f.write(r_pdf.content)
    print(f"[OK] PDF gerado com sucesso!")
    print(f"Salvo em: {caminho_saida}")
    print("")
    print("Abra o arquivo na area de trabalho e confira as paginas 6 e 11.")
else:
    print(f"[ERRO] Falha ao gerar PDF. Status: {r_pdf.status_code}")
    print(r_pdf.text)
