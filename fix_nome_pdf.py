import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_nome_pdf")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a linha do Content-Disposition e substitui
trecho_antigo = 'headers={"Content-Disposition": f"inline; filename=relatorio_{periodo}.pdf"}'
trecho_novo = 'headers={"Content-Disposition": f"inline; filename=relato_consolidado_{periodo}.pdf"}'

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    print("✅ Nome do arquivo PDF alterado para 'relato_consolidado_{periodo}.pdf'.")
else:
    print("⚠️ Trecho exato não encontrado. Tentando abordagem alternativa...")
    # Tenta encontrar o padrão de forma mais flexível
    import re
    padrao = r'filename=relatorio_\{periodo\}\.pdf'
    if re.search(padrao, conteudo):
        conteudo = re.sub(padrao, 'filename=relato_consolidado_{periodo}.pdf', conteudo)
        print("✅ Nome do arquivo PDF alterado via regex.")
    else:
        print("❌ Não foi possível localizar a linha do Content-Disposition.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
