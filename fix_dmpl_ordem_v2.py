import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_ordem_utf8")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Troca a chave "DMPL" pelo nome amigável que a API retorna no JSON
old = '("DMPL", "7. Demonstração das Mutações do Patrimônio Líquido (DMPL)"),'
new = '("Demonstração das Mutações do PL (DMPL)", "7. Demonstração das Mutações do Patrimônio Líquido (DMPL)"),'

if old in conteudo:
    conteudo = conteudo.replace(old, new)
    print("✅ ordem_modelo: chave 'DMPL' trocada por 'Demonstração das Mutações do PL (DMPL)'.")
else:
    print("⚠️ Linha exata não encontrada. Tentando replace por regex...")
    import re
    padrao = re.compile(r'\("DMPL",\s*"7\.[^"]*"\),')
    novo_conteudo, n = padrao.subn(new, conteudo, count=1)
    if n > 0:
        conteudo = novo_conteudo
        print(f"✅ ordem_modelo: substituído via regex ({n} ocorrência).")
    else:
        print("❌ Nenhuma ocorrência encontrada nem via regex.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"
cd "C:\Users\Marcelo Medeiros\pc_sistema"
@'
import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_ordem_v2")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

old = '("DMPL", "7. Demonstração das Mutações do Patrimônio Líquido (DMPL)"),'
new = '("Demonstração das Mutações do PL (DMPL)", "7. Demonstração das Mutações do Patrimônio Líquido (DMPL)"),'

if old in conteudo:
    conteudo = conteudo.replace(old, new)
    print("✅ ordem_modelo: chave 'DMPL' trocada por 'Demonstração das Mutações do PL (DMPL)'.")
else:
    print("❌ Linha não encontrada no formato exato. Nada foi alterado.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
