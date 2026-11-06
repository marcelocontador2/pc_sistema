import re

c = open(r"pc_frontend\index.html", encoding='utf-8').read()

print("=" * 70)
print("DIAGNÓSTICO: ESTRUTURA DA TABELA DE RELATÓRIOS")
print("=" * 70)

# Mostra o trecho onde a tabela é montada
idx = c.find('tbody.innerHTML')
if idx != -1:
    print("--- TRECHO DA MONTAGEM DA TABELA ---")
    print(c[max(0, idx-300):idx+800])
else:
    print("[AVISO] 'tbody.innerHTML' não encontrado")

# Procura a função que carrega os relatórios
idx2 = c.find('/api/relatorios_importados')
if idx2 != -1:
    print("\n--- TRECHO DA FUNÇÃO QUE CARREGA OS RELATÓRIOS ---")
    print(c[max(0, idx2-300):idx2+1200])
else:
    print("[AVISO] '/api/relatorios_importados' não encontrado")
