import re
import ast
import shutil

# --- PARTE 1: Corrigir o Backend (main.py) ---
print("🔧 [1/2] CORRIGINDO O BACKEND (main.py)...")
caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bf_condicao_final")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o loop de verificação dos módulos
padrao = r'(for chave, tabela in modulos\.items\(\):\s*try:\s*)(cursor\.execute\([^\n]+\))'
match = re.search(padrao, conteudo, re.DOTALL)

if match:
    # Substitui o bloco para incluir a condição do BF
    novo_bloco = (
        'for chave, tabela in modulos.items():\n'
        '            try:\n'
        '                if chave == "analise_financeira_bf":\n'
        '                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))\n'
        '                else:\n'
        '                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))\n'
    )
    # Pega o resto do bloco (até o cursor.fetchone())
    resto_idx = match.end()
    resto = conteudo[resto_idx:resto_idx+200]
    
    conteudo = conteudo[:match.start()] + novo_bloco + conteudo[resto_idx:]
    print("✅ Condição especial para o BF (LIKE) inserida corretamente.")
else:
    print("⚠️ Loop de verificação não encontrado no formato esperado. Tentando abordagem alternativa...")
    # Abordagem alternativa: procura a linha do execute genérico
    linha_antiga = 'cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))'
    if linha_antiga in conteudo:
        # Encontra a indentação da linha
        linhas = conteudo.split('\n')
        for i, l in enumerate(linhas):
            if linha_antiga in l:
                indent = len(l) - len(l.lstrip())
                novo_bloco = (
                    ' ' * indent + 'if chave == "analise_financeira_bf":\n' +
                    ' ' * (indent + 4) + 'cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))\n' +
                    ' ' * indent + 'else:\n' +
                    ' ' * (indent + 4) + linha_antiga + '\n'
                )
                linhas[i] = novo_bloco.rstrip('\n')
                conteudo = '\n'.join(linhas)
                print("✅ Condição do BF inserida via abordagem alternativa.")
                break
        else:
            print("❌ Linha do execute genérico não encontrada.")
    else:
        print("❌ Nenhuma das abordagens funcionou. O BF não será corrigido no backend.")

# Verifica a sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe: {e.lineno}: {e.text}")
    print("⚠️ NÃO salvando o arquivo para não quebrar o servidor.")

# --- PARTE 2: Corrigir o HTML ---
print("\n🔧 [2/2] CORRIGINDO O HTML (relatorio_consolidado.html)...")
caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_undefined_final")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui todas as ocorrências da variável
substituicoes = [
    ("data.total_faltando", "data.faltando ? data.faltando.length : 0"),
    ("${data.total_faltando}", "${(data.faltando ? data.faltando.length : 0)}")
]

for antigo, novo in substituicoes:
    if antigo in html:
        html = html.replace(antigo, novo)
        print(f"✅ Substituído: '{antigo}' -> '{novo}'")

with open(caminho_html, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ HTML atualizado.")
