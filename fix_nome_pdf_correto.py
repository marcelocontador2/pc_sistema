import shutil
import ast
import re

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_nome_pdf_correto")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Corrige o nome do arquivo para "relatorio_consolidado_{periodo}.pdf"
conteudo = re.sub(
    r'filename=relato_consolidado_\{periodo\}\.pdf',
    'filename=relatorio_consolidado_{periodo}.pdf',
    conteudo
)
conteudo = re.sub(
    r'filename=relatorio_\{periodo\}\.pdf',
    'filename=relatorio_consolidado_{periodo}.pdf',
    conteudo
)

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ Nome do arquivo corrigido para 'relatorio_consolidado_{periodo}.pdf'.")
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
