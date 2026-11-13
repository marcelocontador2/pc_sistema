import subprocess
import os
import shutil

print("="*70)
print("🔍 BUSCANDO O TEMPLATE DO RELATÓRIO CONSOLIDADO NO GITHUB (10/11/2026)")
print("="*70)

# 1. Verifica se o repositório está configurado
try:
    resultado = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
    print("📌 Remote configurado:")
    print(resultado.stdout)
except Exception as e:
    print(f"❌ Erro ao verificar git: {e}")
    exit()

# 2. Lista os commits do dia 10/11/2026
print("\n📌 Commits do dia 10/11/2026:")
resultado = subprocess.run(
    ["git", "log", "--all", "--since=2026-11-10", "--until=2026-11-11", "--oneline"],
    capture_output=True, text=True
)
if resultado.stdout:
    print(resultado.stdout)
else:
    print("⚠️ Nenhum commit encontrado nessa data. Listando os últimos 10 commits:")
    resultado = subprocess.run(["git", "log", "--oneline", "-10"], capture_output=True, text=True)
    print(resultado.stdout)

# 3. Procura o arquivo de template no histórico
print("\n📌 Buscando o arquivo 'relatorio_consolidado.html' no histórico:")
resultado = subprocess.run(
    ["git", "log", "--all", "--oneline", "--", "pc_frontend/relatorio_consolidado.html"],
    capture_output=True, text=True
)
print(resultado.stdout if resultado.stdout else "⚠️ Arquivo não encontrado no histórico.")

print("\n📌 Buscando templates de PDF no histórico (main.py):")
resultado = subprocess.run(
    ["git", "log", "--all", "--oneline", "--", "pc_backend/main.py"],
    capture_output=True, text=True
)
print(resultado.stdout[:2000] if resultado.stdout else "⚠️ Nenhum commit encontrado.")
