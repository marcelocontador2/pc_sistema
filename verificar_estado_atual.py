import re

c = open(r"pc_frontend\relatorio_centro_custos.html", encoding="utf-8").read()

print("=" * 70)
print("VERIFICAÇÃO DO ESTADO ATUAL DO ARQUIVO")
print("=" * 70)

# 1. A barra de botões está no HTML?
if 'id="barra-edicao-conclusao"' in c:
    print("\n[OK] A barra de botões ESTÁ no HTML.")
    # Mostra o trecho
    idx = c.find('id="barra-edicao-conclusao"')
    print(c[idx-100:idx+600])
else:
    print("\n[FALTA] A barra de botões NÃO está no HTML.")

# 2. O botão específico existe?
if 'id="btn-editar-conclusao"' in c:
    print("\n[OK] O botão 'Editar Conclusão' ESTÁ no HTML.")
else:
    print("\n[FALTA] O botão 'Editar Conclusão' NÃO está no HTML.")

# 3. O h2 tem o título exato?
if '<h2 class="section-title">Conclusão e Recomendações</h2>' in c:
    print("\n[OK] O h2 está com a classe e texto exatos.")
else:
    print("\n[AVISO] O h2 NÃO está com o texto exato. Buscando variações...")
    match = re.search(r'<h2[^>]*>.*?Conclusão.*?</h2>', c, re.IGNORECASE)
    if match:
        print("Encontrado:", match.group(0))
    else:
        print("Nenhum h2 de conclusão encontrado.")

# 4. O script de edição está no final?
if 'js-edicao-final-real' in c:
    print("\n[OK] O script de edição está no arquivo.")
else:
    print("\n[FALTA] O script de edição NÃO está no arquivo.")

# 5. Os blocos ainda têm contenteditable?
if 'contenteditable' in c:
    print("\n[AVISO] Ainda há 'contenteditable' no HTML (pode ser de tentativas antigas).")
else:
    print("\n[OK] Nenhum 'contenteditable' residual no HTML.")
