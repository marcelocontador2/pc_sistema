import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. QUANTOS BLOCOS <script> EXISTEM? ===")
scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', s, re.DOTALL | re.IGNORECASE)
print(f"Total: {len(scripts)}")

for i, script in enumerate(scripts):
    print(f"\n--- Script {i+1} ---")
    print(f"Tamanho: {len(script)} caracteres")
    if "function carregarHistorico" in script:
        print("  -> Contem carregarHistorico.")
    if "function carregarPanorama" in script:
        print("  -> Contem carregarPanorama.")
    if "function exibirSelecionado" in script:
        print("  -> Contem exibirSelecionado.")
    # Mostra as primeiras linhas
    linhas = script.strip().split("\n")
    print(f"  Primeira linha: {linhas[0] if linhas else 'vazio'}")

print("\n=== 2. O SCRIPT ESTA NO LUGAR CERTO? ===")
# Verifica se o script foi inserido antes do </body>
if "</body>" in s and "<script>" in s:
    pos_script = s.find("<script>")
    pos_body = s.find("</body>")
    if pos_script < pos_body:
        print("  OK: O script esta antes do </body>.")
    else:
        print("  ERRO: O script esta DEPOIS do </body> ou fora do lugar.")
else:
    print("  AVISO: Nao foi possivel verificar a posicao.")
