import re

arq = r"pc_frontend\relatorio_consolidado_template.html"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove o script visual que injetamos no final da página
html = re.sub(r"<script>\s*document\.addEventListener\('DOMContentLoaded'.*?</script>", "", html, flags=re.DOTALL)

# 2. Remove o bloco "Ranking de Gastos" que o script de Python tentou inserir
# (Remove desde o comentário até o fechamento do tab de ranking)
html = re.sub(r"// --- Ranking de Gastos \(Ordem Decrescente\) ---.*?H \+= tab\(\['#', 'Centro de Custo', 'Gasto Atual', 'Variação \(%\)'\], rowsRanking\);", "", html, flags=re.DOTALL)

# 3. Remove a variável const que o script tentou criar
html = re.sub(r"const varTabela = \"VAR_TABELA_AQUI\";", "", html)
html = re.sub(r"const varTabela = \"rows\";", "", html)

# 4. Remove o bloco de nota (caso ainda exista de scripts antigos)
html = re.sub(r"// --- Destaque Maior Gasto ---.*?H \+= '</div>';", "", html, flags=re.DOTALL)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Limpeza concluída. Todos os códigos de ranking foram removidos do template.")
