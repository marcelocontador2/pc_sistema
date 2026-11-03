import re

c = open(r"pc_frontend\panorama.html", encoding="utf-8-sig").read()

print("=" * 70)
print("CORPO DAS FUNÇÕES JAVASCRIPT DO PANORAMA")
print("=" * 70)

for func in ["carregarPanorama", "aplicarValores", "gerarPDF"]:
    match = re.search(rf'function {func}\([^)]*\) \{{(.*?)\n        \}}', c, re.DOTALL)
    if match:
        print(f"\n--- {func} ---")
        print(match.group(1)[:1000])
    else:
        print(f"\n[AVISO] Função {func} não encontrada.")
