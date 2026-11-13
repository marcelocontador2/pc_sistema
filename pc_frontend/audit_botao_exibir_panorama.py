import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. BOTOES DA TELA ===")
botoes = re.findall(r'<button[^>]*>([^<]*)</button>', s)
for b in botoes:
    # Pega a tag inteira
    match = re.search(r'<button[^>]*>' + re.escape(b) + r'</button>', s)
    if match:
        print(f"  {match.group(0)}")

print("\n=== 2. O SCRIPT VINCULA O BOTAO EXIBIR? ===")
if "btn-exibir" in s:
    print("SIM, o ID btn-exibir existe no HTML.")
else:
    print("NAO, o ID btn-exibir nao existe. O botao pode ter outra classe/ID.")

if "btnExibir.addEventListener" in s:
    print("SIM, o JS esta tentando vincular o evento ao btnExibir.")
else:
    print("NAO, o JS NAO esta vinculando o evento ao btnExibir.")
