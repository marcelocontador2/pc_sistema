import re

c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Lista de IDs usados no JavaScript
ids_usados = [
    'tela-dashboard', 'menu-dashboard', 'tela-demonstracoes', 'menu-demonstracoes',
    'tela-upload', 'menu-upload', 'upload-tipo', 'upload-arquivo', 'upload-ano',
    'upload-mes', 'upload-trimestre', 'upload-exercicio', 'msg-upload', 'form-upload',
    'filtro-periodo'
]

print("=== VERIFICAÇÃO DE IDs NO HTML ===")
for id_usado in ids_usados:
    if f'id="{id_usado}"' in c:
        print(f"[OK] id='{id_usado}' encontrado.")
    else:
        print(f"[ERRO] id='{id_usado}' NÃO encontrado no HTML!")

# Verifica se a div de upload existe
if 'tela-upload' in c:
    print("\n[INFO] A tela de upload está presente no HTML.")
else:
    print("\n[ERRO] A tela de upload NÃO está no HTML!")
