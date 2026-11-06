import re

arquivo = r"pc_frontend\panorama.html"
with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

print("=== 1) HTML DOS BOTOES (Verificar, Gerar PDF, Salvar) ===")
# Busca as tags <button> que contenham esses textos
for m in re.finditer(r'<button[^>]*>.*?(Verificar|Gerar PDF|Confirmar e Salvar).*?</button>', html, re.IGNORECASE | re.DOTALL):
    # Pega a tag de abertura completa
    tag_completa = re.search(r'<button[^>]*>', m.group(0)).group(0)
    print(tag_completa)
    print("-" * 50)

print("\n=== 2) CORPO DAS FUNCOES JS ===")
funcs = ["function carregarPanorama", "function salvarPanorama", "function gerarPDFPanorama"]
for fn in funcs:
    idx = html.find(fn)
    if idx != -1:
        # Pega 30 linhas ou até a próxima function
        end = html.find("function ", idx + 10)
        if end == -1: end = idx + 1500
        bloco = html[idx:end].strip()
        print(bloco[:1500]) # Limita o tamanho para não lotar a tela
        print("\n" + "="*50 + "\n")
    else:
        print(f"[ALERTA] {fn} NAO ENCONTRADA no arquivo!\n")
