import os

print("=" * 70)
print("1) O DIRETORIO UPLOAD_DIR EXISTE?")
print("=" * 70)
# O UPLOAD_DIR e definido no main.py como: os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
caminho = os.path.join(os.path.dirname(os.path.abspath("pc_backend/main.py")), "..", "pc_storage", "uploads_raw")
caminho = os.path.abspath(caminho)
print(f"Caminho esperado: {caminho}")
if os.path.exists(caminho):
    print("[OK] O diretorio existe.")
else:
    print("[ERRO] O diretorio NAO existe! Criando...")
    os.makedirs(caminho, exist_ok=True)
    print("[OK] Diretorio criado.")

print("\n" + "=" * 70)
print("2) TESTANDO CONEXAO COM O SERVIDOR")
print("=" * 70)
import requests
try:
    response = requests.get("http://127.0.0.1:9994/", timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("[OK] O servidor esta respondendo.")
    else:
        print("[AVISO] O servidor respondeu, mas com status inesperado.")
except requests.exceptions.Timeout:
    print("[ERRO] O servidor nao respondeu em 5 segundos (travado).")
except requests.exceptions.ConnectionError:
    print("[ERRO] Nao foi possivel conectar ao servidor (nao esta rodando).")
except Exception as e:
    print(f"[ERRO] {e}")

print("\n" + "=" * 70)
print("3) TESTANDO A ROTA /api/relatorios_importados")
print("=" * 70)
try:
    response = requests.get("http://127.0.0.1:9994/api/relatorios_importados", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text[:200]}")
except Exception as e:
    print(f"[ERRO] {e}")

print("\n" + "=" * 70)
print("4) TESTANDO A ROTA /upload (com arquivo pequeno de teste)")
print("=" * 70)
import io

# Cria um CSV de teste pequeno na memoria
csv_teste = "TESTE;VALOR\nA;1\nB;2\n"
files = {"file": ("teste_upload.csv", io.BytesIO(csv_teste.encode("utf-8")), "text/csv")}
data = {
    "tipo_relatorio": "BALANCO_PATRIMONIAL",
    "ano": "2026",
    "periodo_tipo": "TRIMESTRE",
    "periodo_valor": "3"
}
try:
    response = requests.post("http://127.0.0.1:9994/upload", files=files, data=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text[:500]}")
    if response.status_code == 200:
        print("[OK] A rota /upload respondeu corretamente!")
    else:
        print("[ERRO] A rota /upload retornou erro.")
except requests.exceptions.Timeout:
    print("[ERRO] A rota /upload travou (nao respondeu em 10 segundos).")
except Exception as e:
    print(f"[ERRO] {e}")
