from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Encontrar e remover o page.evaluate do PDF completo
inicio_completo = conteudo.find('await page.evaluate(f"""')
if inicio_completo == -1:
    print("AVISO: nao achei o page.evaluate")
else:
    # Encontrar o fim do page.evaluate
    fim_completo = conteudo.find('""")', inicio_completo)
    if fim_completo != -1:
        # Remover o bloco (desde "await page.evaluate" ate '""")')
        conteudo = conteudo[:inicio_completo] + 'pass  # Dados injetados via fetch no HTML' + conteudo[fim_completo + 4:]
        print("OK: page.evaluate removido!")

# 2. Garantir que as rotas so esperam o fetch (sem injecao)
# (o page.wait_for_timeout ja existe)

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
