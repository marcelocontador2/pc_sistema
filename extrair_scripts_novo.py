import re
c = open('pc_frontend/index.html', encoding='utf-8-sig').read()
scripts = re.findall(r'<script>(.*?)</script>', c, re.DOTALL)
for i, script in enumerate(scripts):
    with open(f'script_{i}.js', 'w', encoding='utf-8') as f:
        f.write(script)
print(f"[OK] {len(scripts)} blocos extraídos.")
