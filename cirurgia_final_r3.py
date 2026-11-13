import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_cirurgia_final")

with open(caminho_main, "r", encoding="utf-8") as f:
    linhas = f.readlines()

print("🔧 Removendo todas as linhas problemáticas com 'r[3]'...")

# A linha problemática exata (que quebra se vier menos colunas)
linha_problematica = 'return [{"id": r[0], "periodo": r[1], "data_geracao": r[2], "dados": r[3]} for r in rows]'

# Substitui por uma versão segura
linha_segura = '''return [{"id": r[0], "periodo": r[1], "data_geracao": r[2], "dados": r[3] if len(r) > 3 else "{}"} for r in rows]'''

count = 0
for i, linha in enumerate(linhas):
    if linha_problematica in linha:
        linhas[i] = linha.replace(linha_problematica, linha_segura)
        count += 1
        print(f"✅ Linha {i+1} corrigida (versão à prova de falhas).")

if count == 0:
    print("⚠️ Nenhuma linha problemática exata encontrada. Tentando abordagem flexível...")
    # Tenta substituir qualquer linha que tenha "r[3]" sem "if len(r)"
    for i, linha in enumerate(linhas):
        if 'r[3]' in linha and 'if len(r)' not in linha:
            linhas[i] = linha.replace('r[3]', 'r[3] if len(r) > 3 else "{}"')
            count += 1
            print(f"✅ Linha {i+1} corrigida via abordagem flexível.")

conteudo = "".join(linhas)

# Verifica a sintaxe
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"✅ {count} linha(s) corrigida(s). Sintaxe OK.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
