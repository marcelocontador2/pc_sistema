import re
import shutil

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

shutil.copy(caminho, caminho + ".bak_debug_api")

# Localiza a função api_comparativo_receitas_v2 (primeira ocorrência)
padrao = r'@app\.get\("/api/comparativo_receitas_v2/\{periodo\}"\)\s*\ndef\s+api_comparativo_receitas_v2\(periodo:\s*str\):'
match = re.search(padrao, content)

if not match:
    print("❌ Rota não encontrada.")
    exit()

# Adiciona um print de diagnóstico no início da função
inicio_funcao = match.end()
# Pula a primeira linha em branco, se houver
pos = inicio_funcao
while pos < len(content) and content[pos] in " \t\n\r":
    pos += 1

# Insere um print para debug
debug_print = '    print(f"[DEBUG API V2] Chamada com periodo={periodo}")\n'
content = content[:pos] + debug_print + content[pos:]

# Encontra o bloco try/except dentro da função e adiciona um traceback no except
# Procura o retorno do erro
padrao_except = r'(except Exception as e:\s*\n\s*print\(f"\[ERRO\] Falha ao ler CSV \{arquivo\}: \{e\}"\)\s*\n\s*return None)'
if re.search(padrao_except, content):
    content = re.sub(
        padrao_except,
        r'except Exception as e:\n            import traceback; traceback.print_exc()\n            return None',
        content
    )
    print("✅ Bloco except aprimorado com traceback.")
else:
    print("⚠️ Não encontrei o padrão do except para adicionar traceback.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Debug adicionado na API.")
