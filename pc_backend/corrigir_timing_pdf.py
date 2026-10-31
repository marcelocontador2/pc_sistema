from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. PDF Completo: adicionar espera apos o goto
trecho_completo = '''await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}")'''
novo_completo = '''await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}")
                await page.wait_for_timeout(2000)  # Espera o fetch terminar'''

if trecho_completo in conteudo:
    conteudo = conteudo.replace(trecho_completo, novo_completo, 1)
    print("OK: Espera adicionada no PDF completo!")
else:
    print("AVISO: nao achei o goto do PDF completo")

# 2. PDF Resumo: adicionar espera apos o goto
trecho_resumo = '''await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}")'''
novo_resumo = '''await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}")
                await page.wait_for_timeout(2000)  # Espera o fetch terminar'''

if trecho_resumo in conteudo:
    conteudo = conteudo.replace(trecho_resumo, novo_resumo, 1)
    print("OK: Espera adicionada no PDF resumo!")
else:
    print("AVISO: nao achei o goto do PDF resumo")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
