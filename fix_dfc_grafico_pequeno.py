import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_dfc_grafico_pequeno")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Substitui a tag do canvas do DFC para incluir estilo reduzido
conteudo = conteudo.replace(
    '<div class=\'grafico\'><canvas id=\'chartDFC\'></canvas></div>',
    '<div class=\'grafico\' style=\'max-width: 400px; height: 200px; margin: 10px auto;\'><canvas id=\'chartDFC\' style=\'width: 100%; height: 100%;\'></canvas></div>'
)

# 2. Ajusta as opções do Chart.js para o gráfico do DFC manter proporção
conteudo = conteudo.replace(
    "options: { responsive: true, plugins: { legend: { display: false } } }",
    "options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }"
)

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ Gráfico do item 5 (DFC) reduzido para caber na mesma página.")
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
