import re

c = open(r"pc_frontend\panorama.html", encoding="utf-8").read()

print("=" * 70)
print("INSPEÇÃO DO CÓDIGO HTML DOS BOTÕES")
print("=" * 70)

# 1. Procura onde tem a palavra "Voltar" e mostra o HTML em volta
idx_voltar = c.find('Voltar')
if idx_voltar != -1:
    print("\n--- HTML EM VOLTA DO BOTÃO 'VOLTAR' ---")
    # Pega 300 caracteres antes e 300 depois
    inicio = max(0, idx_voltar - 300)
    fim = min(len(c), idx_voltar + 300)
    print(c[inicio:fim])
else:
    print("Não achei a palavra 'Voltar'.")

# 2. Procura onde tem a palavra "Gerar PDF" e mostra o HTML em volta
idx_pdf = c.find('Gerar PDF')
if idx_pdf != -1:
    print("\n--- HTML EM VOLTA DO BOTÃO 'GERAR PDF' ---")
    inicio = max(0, idx_pdf - 300)
    fim = min(len(c), idx_pdf + 300)
    print(c[inicio:fim])
else:
    print("Não achei a palavra 'Gerar PDF'.")

# 3. Verifica se há erros de script no final do arquivo
print("\n--- ÚLTIMOS 500 CARACTERES DO ARQUIVO ---")
print(c[-500:])
