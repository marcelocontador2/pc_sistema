import re

c = open(r"pc_frontend\panorama.html", encoding="utf-8").read()

print("=" * 70)
print("AUDITORIA DO JAVASCRIPT DA PÁGINA")
print("=" * 70)

# 1. Verifica se as tags <script> estão balanceadas
abre = len(re.findall(r'<script[^>]*>', c, re.IGNORECASE))
fecha = len(re.findall(r'</script>', c, re.IGNORECASE))
print(f"\nTags <script> abertas: {abre}")
print(f"Tags </script> fechadas: {fecha}")
if abre != fecha:
    print("[!!] DESEQUILÍBRIO! Isso quebra TODO o JavaScript da página.")
else:
    print("[OK] Tags balanceadas.")

# 2. Verifica se as funções essenciais existem
print("\n--- FUNÇÕES ESSENCIAIS ---")
for func in ['carregarPanorama', 'salvarPanorama', 'carregarHistorico', 'exibirSelecionado', 'excluirSelecionado', 'gerarPDFPanorama']:
    if f'function {func}' in c:
        print(f"  [OK] {func}")
    else:
        print(f"  [FALTA] {func}")

# 3. Mostra o HTML exato do botão Voltar atual
print("\n--- HTML ATUAL DO BOTÃO VOLTAR ---")
match = re.search(r'<[^>]*>.*?Voltar.*?</[^>]+>', c, re.IGNORECASE | re.DOTALL)
if match:
    print(match.group(0)[:500])
else:
    print("Não achei.")

# 4. Procura por onclick que possam estar quebrados (com caracteres estranhos)
print("\n--- TODOS OS ONCLICK NA PÁGINA ---")
for m in re.finditer(r'onclick="([^"]*)"', c):
    txt = m.group(1)[:80]
    print(f"  {txt}")

# 5. Verifica se o botão está dentro de um <form>
print("\n--- BOTÃO ESTÁ DENTRO DE FORM? ---")
idx_btn = c.find('Voltar')
if idx_btn != -1:
    antes = c[:idx_btn]
    if '<form' in antes and '</form>' not in antes:
        print("[!!] SIM, está dentro de um form. Isso pode causar submit.")
    else:
        print("[OK] Não está dentro de form.")
