import os

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("🔍 Procurando todas as ocorrências de 'sqlite_compat' no main.py:")
print("=" * 80)
for i, linha in enumerate(linhas):
    if "sqlite_compat" in linha:
        print(f"   {i+1:5d}: {linha}", end="")

print("\n" + "=" * 80)
print("📁 Conteúdo da pasta pc_backend (arquivos .py):")
print("=" * 80)
for f in sorted(os.listdir("pc_backend")):
    if f.endswith(".py"):
        print(f"   - {f}")

print("\n" + "=" * 80)
print("🔍 Procurando 'sqlite_compat' em TODOS os arquivos .py do projeto:")
print("=" * 80)
for root, dirs, files in os.walk("."):
    # Ignora pastas de venv, backup e __pycache__
    dirs[:] = [d for d in dirs if d not in ("pc_venv", ".git", "__pycache__") and not d.startswith(".")]
    for file in files:
        if file.endswith(".py"):
            caminho_completo = os.path.join(root, file)
            try:
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                if "sqlite_compat" in conteudo:
                    print(f"   Encontrado em: {caminho_completo}")
            except:
                pass
