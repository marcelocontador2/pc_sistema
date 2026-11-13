with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== ESTRUTURA DO SCRIPT NO DMPL (QUE FUNCIONA) ===")
# Encontra todos os blocos <script>
import re
scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', s, re.DOTALL | re.IGNORECASE)
print(f"Quantidade de blocos <script>: {len(scripts)}")
for i, script in enumerate(scripts):
    print(f"\n--- Script {i+1} (primeiras 3 linhas) ---")
    linhas = script.strip().split("\n")
    for l in linhas[:3]:
        print(f"  {l.strip()}")

print("\n=== O DMPL TEM O CHART.JS INJETADO? ===")
if "cdn.jsdelivr.net/npm/chart.js" in s:
    print("  SIM, o DMPL tem o Chart.js via CDN.")
elif "chart.js" in s.lower():
    print("  SIM, o DMPL menciona Chart.js (pode ser local).")
else:
    print("  NÃO, o DMPL não tem Chart.js explicitamente no HTML (pode estar em outro arquivo).")
