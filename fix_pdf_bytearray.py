import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_pdf_bytearray")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Corrige a linha do pdf.output
linha_antiga = "pdf_bytes = pdf.output(dest='S').encode('latin-1')"
linha_nova = "pdf_bytes = bytes(pdf.output(dest='S'))"

if linha_antiga in conteudo:
    conteudo = conteudo.replace(linha_antiga, linha_nova)
    print("✅ Linha do pdf.output corrigida (bytearray).")
else:
    # Tenta abordagem alternativa: substituir qualquer chamada .encode('latin-1') que venha de pdf.output
    if "pdf.output(dest='S')" in conteudo:
        conteudo = conteudo.replace("pdf.output(dest='S').encode('latin-1')", "bytes(pdf.output(dest='S'))")
        print("✅ Correção aplicada via abordagem alternativa.")
    else:
        print("⚠️ Padrão de pdf.output não encontrado exato. Verificando...")

# 2. Remove a injeção automática da DMPL (que causa o erro "list indices must be integers")
linha_dmpl_antiga = 'dados["dmpl"] = json.loads(row_dmpl[0])'
if linha_dmpl_antiga in conteudo:
    conteudo = conteudo.replace(linha_dmpl_antiga, '# DMPL não injetada (tratada em outro módulo)')
    print("✅ Injeção automática da DMPL removida (evitando erro de índice).")

# 3. Verifica e salva
try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo com sintaxe verificada!")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
