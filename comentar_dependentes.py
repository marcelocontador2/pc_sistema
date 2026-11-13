import shutil
import re

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

shutil.copy(caminho, caminho + ".bak_dependentes_removidos")

# Lista de nomes que foram perdidos ao comentar os imports
nomes_removidos = [
    "dfc", "panorama_router", "dvp_router", "bf_router",
    "api_analise_dfc", "processar_bf", "processar_dvp",
    "DB_CONFIG", "routers"
]

alterado = False
print("🔧 Comentando linhas que dependem dos imports removidos:")

for i, linha in enumerate(linhas):
    # Ignora linhas que já estão comentadas
    if linha.strip().startswith("#"):
        continue

    # Verifica se a linha usa algum dos nomes removidos (fora de strings)
    for nome in nomes_removidos:
        # Procura o nome como palavra isolada (evita pegar 'dfc' dentro de 'dfc_foo')
        if re.search(r'\b' + re.escape(nome) + r'\b', linha):
            # Verifica se não é uma definição de variável/função (def nome, nome =)
            if not re.match(r'^\s*(def|class|async def)\s+' + re.escape(nome) + r'\b', linha) and \
               not re.match(r'^\s*' + re.escape(nome) + r'\s*=', linha):
                nova = "# [REMOVIDO - dependente de import quebrado] " + linha
                print(f"   Linha {i+1}: {linha.strip()[:80]}  →  COMENTADA")
                linhas[i] = nova
                alterado = True
                break

if alterado:
    with open(caminho, "w", encoding="utf-8") as f:
        f.writelines(linhas)
    print("\n✅ Linhas dependentes comentadas.")
else:
    print("\n⚠️ Nenhuma linha dependente encontrada.")

# Verifica a sintaxe
try:
    with open(caminho, "r", encoding="utf-8") as f:
        compile(f.read(), caminho, "exec")
    print("✅ Arquivo main.py está sintaticamente válido!")
except SyntaxError as e:
    print(f"\n❌ Erro de sintaxe na linha {e.lineno}: {e.msg}")
    print(f"   Texto: {e.text}")
