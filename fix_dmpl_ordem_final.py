import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_ordem_final")

with open(caminho, "r", encoding="utf-8") as f:
    linhas = f.readlines()

alterado = False
for i, linha in enumerate(linhas):
    # Procura a linha do ordem_modelo que começa com ("DMPL",
    if linha.strip().startswith('("DMPL",'):
        # Extrai o segundo elemento (o título de exibição) mantendo-o intacto
        # Formato:        ("DMPL", "7. Título..."),
        partes = linha.split('", "', 1)
        if len(partes) == 2:
            titulo_resto = partes[1]  # '7. Demonstração... (DMPL)"),\n'
            nova_linha = '        ("Demonstração das Mutações do PL (DMPL)", "' + titulo_resto
            linhas[i] = nova_linha
            alterado = True
            print(f"✅ Linha {i+1} alterada.")
            print(f"   Antes: {linha.strip()}")
            print(f"   Depois: {nova_linha.strip()}")
            break

if not alterado:
    print("❌ Linha do ordem_modelo com '(\"DMPL\",' não encontrada.")

conteudo = "".join(linhas)

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
