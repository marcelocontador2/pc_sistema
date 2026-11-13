import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_grafico_altura")

# 1. Ajusta o canvas para ter uma altura controlada (ex: 300px) e nao estourar
s = re.sub(r'<canvas[^>]*id="graf"[^>]*>', '<canvas id="graf" style="max-height: 300px; width: 100%;"></canvas>', s)

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK: Altura do canvas ajustada no HTML.")

# 2. Ajusta o JS para permitir proporcao correta e limitar a altura
js_path = "dmpl_functions.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Garante que a altura nao vai estourar
if "maintainAspectRatio: false" in js:
    js = js.replace("maintainAspectRatio: false", "maintainAspectRatio: true")
    
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("OK: Proporcao do grafico ajustada no JS.")

print("PROCESSO CONCLUIDO! Aperte Ctrl+F5 na tela.")
