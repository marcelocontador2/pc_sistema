import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_debug_exibir")

# Adiciona um console.log dentro da funcao exibirSelecionado
padrao = re.compile(r'function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    func_antiga = match.group(0)
    # Adiciona console.log apos o fetch
    func_nova = func_antiga.replace(
        ".then(dados => {",
        ".then(dados => {\n            console.log('DEBUG exibirSelecionado: dados recebidos =', dados);\n            console.log('DEBUG exibirSelecionado: dados.atual =', dados ? dados.atual : 'dados é null');"
    )
    s = s[:match.start()] + func_nova + s[match.end():]
    print("OK: console.log adicionado na funcao exibirSelecionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
