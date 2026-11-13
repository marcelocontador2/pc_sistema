import shutil

# 1. Backup do arquivo atual
shutil.copy("composicao_receitas_despesas.html", "composicao_receitas_despesas.html.bak_reset_final")

# 2. Le o arquivo da DMPL (que esta funcionando)
with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    html = f.read()

# 3. Faz as substituicoes para virar a Composicao
html = html.replace("Análise DMPL", "Composição de Receitas e Despesas")
html = html.replace("Demonstração das Mutações do Patrimônio Líquido (DMPL)", "Receitas e Despesas Comparativas")

# 3.1 Rotas da API
html = html.replace("/historico_analise_dmpl", "/historico_composicao_receitas_despesas")
html = html.replace("/salvar_analise_dmpl/", "/salvar_composicao_receitas_despesas/")
html = html.replace("/excluir_analise_dmpl/", "/excluir_composicao_receitas_despesas/")
html = html.replace("/gerar_pdf_analise_dmpl/", "/gerar_pdf_composicao_receitas_despesas/")
html = html.replace("/api/analise_dmpl/", "/api/composicao_receitas_despesas/")

# 4. Salva o novo arquivo
with open("composicao_receitas_despesas.html", "w", encoding="utf-8") as f:
    f.write(html)

print("OK: composicao_receitas_despesas.html reescrito com a estrutura da DMPL!")
