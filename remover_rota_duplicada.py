import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_rota_dupla_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

print("=" * 70)
print("REMOVENDO ROTA DUPLICADA ANTIGA")
print("=" * 70)

# Remove a rota antiga (response_class=HTMLResponse) com a função serve_relatorio_comparativo_receitas_v2
padrao_antiga = r'@app\.get\("/relatorio_comparativo_receitas_v2",\s*response_class=HTMLResponse\)\s*\n(?:async\s+)?def\s+serve_relatorio_comparativo_receitas_v2\([^)]*\):.*?(?=\n@app\.|\Z)'

if re.search(padrao_antiga, c, re.DOTALL):
    c = re.sub(padrao_antiga, '', c, flags=re.DOTALL)
    print("[OK] Rota antiga removida (response_class=HTMLResponse)")
else:
    print("[AVISO] Rota antiga não encontrada pelo padrão. Tentando variação...")
    # Fallback: busca por qualquer definição da função antiga
    padrao_fallback = r'@app\.get\("/relatorio_comparativo_receitas_v2"[^)]*\)\s*\n(?:async\s+)?def\s+serve_relatorio_comparativo_receitas_v2\([^)]*\):.*?(?=\n@app\.|\Z)'
    if re.search(padrao_fallback, c, re.DOTALL):
        c = re.sub(padrao_fallback, '', c, flags=re.DOTALL)
        print("[OK] Rota antiga removida via fallback")
    else:
        print("[ERRO] Não consegui encontrar a rota antiga para remover")

# Verifica se sobrou alguma definição duplicada do caminho
print("\n" + "=" * 70)
print("VERIFICANDO ROTAS RESTANTES")
print("=" * 70)

matches = re.finditer(r'@app\.(?:get|post)\(["\']([^"\']*relatorio_comparativo_receitas_v2[^"\']*)["\']', c)
count = 0
for m in matches:
    count += 1
    print(f"  {m.group(0)[:120]}")

print(f"\nTotal de rotas para /relatorio_comparativo_receitas_v2: {count}")

# Valida sintaxe e salva
try:
    ast.parse(c)
    open(back_path, 'w', encoding='utf-8').write(c)
    print("\n[OK] Sintaxe validada e arquivo salvo!")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    print("[AVISO] Arquivo NÃO salvo")

print("\n" + "=" * 70)
print("PRÓXIMOS PASSOS")
print("=" * 70)
print("1. Reinicie o servidor (Ctrl+C e suba novamente)")
print("2. Gere o PDF novamente")
print("3. O Playwright agora deve abrir o arquivo _v2.html (novo)")
