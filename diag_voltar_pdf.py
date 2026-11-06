c = open("pc_frontend/liquidez.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) BOTOES E SEUS ONCLICK (linhas 40-60)")
print("=" * 70)
linhas = c.split("\n")
for i in range(40, min(70, len(linhas))):
    if 'button' in linhas[i].lower() or 'onclick' in linhas[i].lower() or 'voltar' in linhas[i].lower():
        print(f"  {i+1}: {linhas[i].strip()[:200]}")

print("\n" + "=" * 70)
print("2) FUNCAO gerarPDF (definicao)")
print("=" * 70)
idx = c.find("function gerarPDF")
if idx != -1:
    fim = c.find("}", idx) + 1
    print(c[idx:fim])
else:
    print("[AVISO] Funcao gerarPDF nao encontrada.")

print("\n" + "=" * 70)
print("3) EVENTOS DE CLIQUE NO DOCUMENTO (document.addEventListener)")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'addEventListener' in ln and 'click' in ln.lower():
        print(f"  Linha {i}: {ln.strip()[:150]}")
