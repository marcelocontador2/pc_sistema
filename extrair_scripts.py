import re

c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Extrai todos os blocos de script
scripts = re.findall(r'<script>(.*?)</script>', c, re.DOTALL)

# Salva cada bloco em um arquivo separado para analisar
for i, script in enumerate(scripts):
    with open(f'script_{i}.js', 'w', encoding='utf-8') as f:
        f.write(script)

print(f"[OK] {len(scripts)} blocos de script extraídos.")
print("Agora rode o Node.js (se tiver) ou inspecione manualmente os arquivos script_*.js")
