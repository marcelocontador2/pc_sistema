import os

# Lê o arquivo
with open('relatorio_centro_custos_v2.html', 'r', encoding='utf-8-sig') as f:
    c = f.read()

# Corrige o texto do botão (remove o corrompido e coloca o certo)
c = c.replace('ðŸ’¾ Salvar Relatório', '💾 Salvar Relatório')
c = c.replace('ðŸ’¾ Salvar Relatório', '💾 Salvar Relatório')
c = c.replace('Salvar Relatório', 'Salvar Relatório')

# Salva com encoding UTF-8 (sem BOM)
with open('relatorio_centro_custos_v2.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("[OK] Texto do botão corrigido!")
print("[OK] Arquivo salvo com UTF-8!")
