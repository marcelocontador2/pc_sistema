import re

c = open(r"pc_frontend\analise_centro_custos.html", encoding="utf-8").read()

print("=" * 70)
print("AUDITORIA DO MODAL")
print("=" * 70)

# Verifica se o modal novo foi aplicado
if 'id="lista-blocos-modal"' in c:
    print("\n[OK] Modal NOVO está no arquivo (com checkboxes)")
else:
    print("\n[FALTA] Modal NOVO não está no arquivo")
    
if 'id="btn-modal-incluir"' in c:
    print("[OK] Botão 'Incluir Novo Bloco' está no arquivo")
else:
    print("[FALTA] Botão 'Incluir Novo Bloco' não está no arquivo")

if 'id="edit-conclusao-total"' in c:
    print("[AVISO] Ainda tem o campo ANTIGO (edit-conclusao-total)")

# Conta quantos modais existem
modais = len(re.findall(r'<div id="modal-conclusao"', c))
print(f"\nQuantidade de modais no arquivo: {modais}")

# Conta quantos scripts de modal
scripts = len(re.findall(r'<script id="js-modal-conclusao"', c))
print(f"Quantidade de scripts js-modal-conclusao: {scripts}")

# Mostra os 500 primeiros caracteres do primeiro modal
idx = c.find('<div id="modal-conclusao"')
if idx != -1:
    print("\n--- TRECHO DO MODAL ---")
    print(c[idx:idx+800])
