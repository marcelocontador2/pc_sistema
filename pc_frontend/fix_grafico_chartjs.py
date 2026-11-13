import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_chartjs")

# 1. Injeta o Chart.js no <head> (se nao existir)
if "cdn.jsdelivr.net/npm/chart.js" not in s:
    s = s.replace("<head>", '<head>\n    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>', 1)
    print("OK: Chart.js injetado no <head>.")

# 2. Atualiza o JavaScript para usar o canvas 'graf' em vez de 'graficoDMPL'
js_path = "dmpl_functions.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui o trecho que busca o canvas
js = js.replace("document.getElementById('graficoDMPL')", "document.getElementById('graf')")

# Se nao achou o grafico, tenta buscar por 'grafico'
if "getElementById('graf')" not in js:
    js = js.replace("document.querySelector('canvas')", "document.getElementById('graf')")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
    print("OK: JavaScript atualizado para usar o canvas 'graf'.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
    print("OK: HTML salvo com Chart.js.")

print("\nPROCESSO CONCLUIDO! Aperte Ctrl+F5 na tela e teste o Exibir.")
