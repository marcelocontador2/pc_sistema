import os, re

print("=" * 70)
print("CAÇADA: ONDE ESTÁ A MENSAGEM DE ERRO 'Erro ao buscar dados do painel'")
print("=" * 70)

# Procura em todos os arquivos .py do projeto
for dirpath, dirnames, filenames in os.walk("."):
    # Ignora pastas de backup e venv
    if "venv" in dirpath or "backup" in dirpath or "__pycache__" in dirpath:
        continue
        
    for f in filenames:
        if f.endswith(".py"):
            caminho = os.path.join(dirpath, f)
            try:
                c = open(caminho, encoding='utf-8-sig').read()
                if "Erro ao buscar dados do painel" in c:
                    print(f"\n[ENCONTRADO] Arquivo: {caminho}")
                    for i, linha in enumerate(c.splitlines(), 1):
                        if "Erro ao buscar dados do painel" in linha:
                            print(f"  Linha {i}: {linha.strip()}")
            except:
                pass

print("\n" + "=" * 70)
print("ROTAS DE PDF DO PANORAMA ATIVAS NO MAIN.PY")
print("=" * 70)
c_main = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
rotas = re.findall(r'(@app\.get\("/gerar_pdf_panorama/[^"]+"\)\s*\n(?:async\s+)?def\s+([a-zA-Z0-9_]+)\([^)]*\):)', c_main, re.IGNORECASE)
for r in rotas:
    print(r[0])
if not rotas:
    print("Nenhuma rota de PDF do panorama encontrada no main.py atual.")
