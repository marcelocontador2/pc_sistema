import re

c = open(r"pc_frontend\relatorio_centro_custos.html", encoding="utf-8").read()

print("=" * 70)
print("INSPEÇÃO DA SEÇÃO DE CONCLUSÃO")
print("=" * 70)

# Procura por qualquer coisa que tenha "Conclusão" no texto
idx = c.find("Conclusão")
if idx == -1:
    idx = c.find("CONCLUSÃO")

if idx != -1:
    # Mostra 2000 chars antes e 3000 depois
    inicio = max(0, idx - 2000)
    fim = min(len(c), idx + 3000)
    print(c[inicio:fim])
else:
    print("[ERRO] Não achei a palavra Conclusão no arquivo.")

print("\n" + "=" * 70)
print("VERIFICANDO SE OS BOTÕES DE EDIÇÃO ESTÃO NO ARQUIVO")
print("=" * 70)
if 'id="btn-editar-conclusao"' in c:
    print("[OK] O botão 'btn-editar-conclusao' está no arquivo.")
    # Mostra o trecho
    idx_btn = c.find('id="btn-editar-conclusao"')
    print(c[max(0, idx_btn-500):idx_btn+500])
else:
    print("[ERRO] O botão NÃO está no arquivo.")

if 'id="barra-edicao-conclusao"' in c:
    print("\n[OK] A barra de edição está no arquivo.")
else:
    print("\n[ERRO] A barra de edição NÃO está no arquivo.")
