import re

arquivo = r"pc_frontend\analise_financeira_bf.html"
c = open(arquivo, encoding='utf-8').read()

print("=" * 70)
print("DIAGNÓSTICO DO BOTÃO PDF - ANÁLISE FINANCEIRA BF")
print("=" * 70)

# 1. Encontrar todos os botões que contenham "Gerar PDF"
botoes = re.findall(r'<button[^>]*>.*?Gerar PDF.*?</button>', c, re.IGNORECASE | re.DOTALL)
print(f"\n[1] Botões encontrados com texto 'Gerar PDF': {len(botoes)}")
for i, btn in enumerate(botoes):
    print(f"  Botão {i+1}: {btn[:200]}")

# 2. Encontrar todas as chamadas onclick que mencionem PDF ou gerarPDF
onclicks = re.findall(r'onclick="([^"]*)"', c, re.IGNORECASE)
onclicks_pdf = [oc for oc in onclicks if 'pdf' in oc.lower()]
print(f"\n[2] Chamadas onclick relacionadas a PDF: {len(onclicks_pdf)}")
for oc in onclicks_pdf:
    print(f"  onclick=\"{oc}\"")

# 3. Verificar se a função gerarPDFFinanceiro está definida
if 'function gerarPDFFinanceiro' in c:
    print("\n[3] Função 'gerarPDFFinanceiro' encontrada.")
    # Mostra o trecho da função
    match = re.search(r'function gerarPDFFinanceiro\(\) \{.*?\n        \}', c, re.DOTALL)
    if match:
        print(match.group(0)[:500])
else:
    print("\n[3] Função 'gerarPDFFinanceiro' NÃO encontrada!")

# 4. Verificar se há múltiplas tag <script> e se estão bem fechadas
scripts_abertos = len(re.findall(r'<script[^>]*>', c))
scripts_fechados = len(re.findall(r'</script>', c))
print(f"\n[4] Tags <script> abertas: {scripts_abertos}, fechadas: {scripts_fechados}")
if scripts_abertos != scripts_fechados:
    print("  [AVISO] Há desequilíbrio nas tags <script>! Isso pode quebrar o JavaScript.")

# 5. Verificar se há erro de sintaxe óbvio no final do arquivo
print("\n[5] Últimos 500 caracteres do arquivo:")
print(c[-500:])
