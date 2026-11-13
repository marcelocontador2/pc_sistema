import re

with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. HTML DO BOTAO 'VERIFICAR DADOS' ===")
btn = re.search(r'<button[^>]*>([^<]*Verificar[^<]*)</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao 'Verificar' nao encontrado no HTML.")

print("\n=== 2. A FUNCAO 'carregar()' ESTA DEFINIDA NO HTML (inline)? ===")
if "function carregar()" in s:
    print("SIM, a funcao carregar() esta no HTML inline.")
else:
    print("NAO, a funcao carregar() NAO esta no HTML inline.")

print("\n=== 3. O BOTAO CHAMA 'carregar()'? ===")
if 'onclick="carregar()"' in s:
    print("SIM, o botao chama carregar().")
else:
    print("NAO, o botao NAO chama carregar().")
