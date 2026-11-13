import ast
import shutil

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_limpeza_definitiva")

with open(caminho_main, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("🔍 Localizando TODAS as funções 'get_hist_consolidado' no main.py...")

# Encontra todas as linhas onde a função é definida
linhas_funcao = []
for i, linha in enumerate(linhas):
    if 'def get_hist_consolidado' in linha:
        linhas_funcao.append(i)

print(f"   Encontradas {len(linhas_funcao)} definição(ões) nas linhas: {[i+1 for i in linhas_funcao]}")

if len(linhas_funcao) > 1:
    print("\n⚠️ Há duplicatas! Removendo todas as versões antigas...")
    # Vamos manter apenas a primeira (que já foi corrigida na linha 3442)
    # Remover as demais
    linhas_remover = set()
    for idx in linhas_funcao[1:]:  # Todas exceto a primeira
        # Encontra o final da função (próxima def ou decorador)
        fim = idx + 1
        while fim < len(linhas) and not (linhas[fim].strip().startswith('def ') or linhas[fim].strip().startswith('@') or linhas[fim].strip().startswith('async def ')):
            fim += 1
        for j in range(idx, fim):
            linhas_remover.add(j)
        print(f"   Removendo função da linha {idx+1} até {fim}")
    
    # Remove as linhas
    linhas = [l for i, l in enumerate(linhas) if i not in linhas_remover]
    print(f"✅ {len(linhas_remover)} linha(s) removida(s).")

conteudo = "".join(linhas)

# Verifica a sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada!")
    
    # Verifica se ainda há a linha problemática
    with open(caminho_main, "r", encoding="utf-8") as f:
        novo_conteudo = f.read()
    if 'r[3]' in novo_conteudo and 'if len(r)' not in novo_conteudo:
        print("⚠️ Ainda há linhas com r[3] sem proteção. Vou corrigir agora...")
        novo_conteudo = novo_conteudo.replace('r[3]', 'r[3] if len(r) > 3 else "{}"')
        with open(caminho_main, "w", encoding="utf-8") as f:
            f.write(novo_conteudo)
        print("✅ Correção extra aplicada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
