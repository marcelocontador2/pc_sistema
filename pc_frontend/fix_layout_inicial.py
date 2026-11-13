import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_header_inicial")

# 1. Ajusta o cabecalho da tabela que aparece ao carregar a pagina
# Procura o <thead> e substitui as colunas antigas pelas novas
padrao_thead = re.compile(r'<thead>.*?</thead>', re.DOTALL | re.IGNORECASE)
novo_thead = '''<thead>
            <tr>
                <th style="text-align:left;">Conta</th>
                <th style="text-align:right;">Valor (R$)</th>
                <th style="text-align:right;">% do Total</th>
            </tr>
        </thead>'''
s, n1 = padrao_thead.subn(novo_thead, s)

# 2. Ajusta a mensagem inicial do tbody para 3 colunas
s = s.replace('<td colspan="4">Clique em Verificar para carregar.</td>', '<td colspan="3">Clique em Verificar para carregar.</td>')
s = s.replace('<td colspan="4" style="text-align:center;">Clique em Verificar para carregar.</td>', '<td colspan="3" style="text-align:center;">Clique em Verificar para carregar.</td>')

# 3. Garante que o canvas do grafico tenha um tamanho fixo para nao ficar espremido
s = re.sub(r'<canvas[^>]*id="graf"[^>]*>', '<canvas id="graf" style="width:100%; height:400px;"></canvas>', s)

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
    
print(f"OK: Cabecalho inicial ajustado ({n1} alteracoes).")
print("OK: Canvas do grafico redimensionado.")
print("PROCESSO CONCLUIDO! Aperte Ctrl+F5 na tela.")
