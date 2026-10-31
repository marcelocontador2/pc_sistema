from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Atualizar a URL do Playwright no PDF completo
trecho_antigo = 'await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}")'
trecho_novo = 'await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}")'

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    print("OK: Playwright do PDF completo atualizado")
else:
    print("AVISO: nao achei o Playwright do PDF completo")

# 2. Atualizar a URL do Playwright no PDF resumo
trecho_antigo2 = 'await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}")'
trecho_novo2 = 'await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}")'

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2)
    print("OK: Playwright do PDF resumo atualizado")
else:
    print("AVISO: nao achei o Playwright do PDF resumo")

# 3. Adicionar o parametro entidade nas assinaturas das funcoes (se ainda nao existir)
if 'def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = "COFEN")' not in conteudo:
    conteudo = conteudo.replace(
        'def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3")',
        'def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = "COFEN")'
    )
    print("OK: Assinatura do PDF completo atualizada")

if 'def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = "COFEN")' not in conteudo:
    conteudo = conteudo.replace(
        'def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3")',
        'def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = "COFEN")'
    )
    print("OK: Assinatura do PDF resumo atualizada")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
