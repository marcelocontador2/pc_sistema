import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. O Chart.js ESTA NA PAGINA? ===")
if "chart.js" in s.lower() or "chart.min.js" in s.lower():
    print("  -> SIM, o Chart.js já está sendo carregado.")
else:
    print("  -> NÃO, o Chart.js NÃO está na página. É por isso que o gráfico está em branco.")

print("\n=== 2. O CANVAS DO GRAFICO EXISTE? ===")
# Procura a div do gráfico e o canvas dentro dela
div_grafico = re.search(r'<div[^>]*>.*?Evolução das Principais Contas.*?</div>', s, re.DOTALL)
if div_grafico:
    print("  -> Div encontrada.")
    print(div_grafico.group(0)[:500])
else:
    print("  -> Div do gráfico NÃO encontrada no HTML.")

# Verifica se existe um canvas com id graficoDMPL ou similar
canvas = re.findall(r'<canvas[^>]*id="([^"]+)"', s)
if canvas:
    print(f"\n  -> Canvas encontrados na página: {canvas}")
else:
    print("\n  -> Nenhum canvas encontrado na página.")
