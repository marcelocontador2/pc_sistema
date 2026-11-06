import os, re

# procura qualquer .py que contenha "FastAPI(" e "@app.get"
candidatos = []
for root, dirs, files in os.walk("."):
    # ignora pastas irrelevantes
    dirs[:] = [d for d in dirs if d not in ("pc_venv", "__pycache__", ".git", "node_modules", "venv", "env")]
    for nome in files:
        if not nome.endswith(".py"):
            continue
        caminho = os.path.join(root, nome)
        try:
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception:
            continue
        if "FastAPI(" in txt and "@app." in txt:
            tem_liquidez = "liquidez" in txt.lower()
            candidatos.append((caminho, os.path.getsize(caminho), tem_liquidez))

print("=== Arquivos que inicializam FastAPI ===")
for c, size, lq in sorted(candidatos, key=lambda x: -x[1]):
    marca = "  <-- TEM 'liquidez'" if lq else ""
    print(f"  {c}  ({size:,} bytes){marca}")

# também lista a raiz pra ver a estrutura
print("\n=== Conteúdo da raiz (pc_sistema) ===")
for item in sorted(os.listdir(".")):
    tipo = "[dir] " if os.path.isdir(item) else "[file]"
    print(f"  {tipo} {item}")
