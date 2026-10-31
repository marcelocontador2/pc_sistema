from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Corrigir URL do PDF completo
trecho_antigo = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&_t=" + str(int(__import__("time").time()))'
trecho_novo = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}&_t=" + str(int(__import__("time").time()))'

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: URL do PDF completo corrigida (com entidade)!")

# 2. Corrigir URL do PDF resumo
trecho_antigo2 = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&_t=" + str(int(__import__("time").time()))'
trecho_novo2 = 'url = f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}&_t=" + str(int(__import__("time").time()))'

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: URL do PDF resumo corrigida (com entidade)!")

# 3. Garantir que a variavel "entidade" existe no escopo
# (ela foi definida na assinatura da funcao, mas vamos confirmar)
if "def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = \"2026-TRIMESTRE-3\", entidade: str = \"COFEN\")" not in conteudo:
    conteudo = conteudo.replace(
        'def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3")',
        'def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = "COFEN")'
    )
    print("OK: entidade adicionada na assinatura do PDF completo!")

if "def gerar_pdf_custo_pessoal(id: int = None, periodo: str = \"2026-TRIMESTRE-3\", entidade: str = \"COFEN\")" not in conteudo:
    conteudo = conteudo.replace(
        'def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3")',
        'def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = "COFEN")'
    )
    print("OK: entidade adicionada na assinatura do PDF resumo!")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
