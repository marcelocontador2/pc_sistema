import shutil

# 1. Backup do arquivo atual
shutil.copy("analise_dmpl.html", "analise_dmpl.html.bak_estrutura_dvp")

# 2. Le o arquivo da DVP (que esta funcionando perfeitamente)
with open("analise_patrimonial.html", "r", encoding="utf-8") as f:
    dvp_html = f.read()

# 3. Faz as substituicoes para transformar DVP em DMPL
dmpl_html = dvp_html

# 3.1 Titulos
dmpl_html = dmpl_html.replace("Análise Patrimonial (DVP)", "Análise DMPL")
dmpl_html = dmpl_html.replace("Demonstração das Variações Patrimoniais (DVP)", "Demonstração das Mutações do Patrimônio Líquido (DMPL)")

# 3.2 Rotas da API
dmpl_html = dmpl_html.replace("/historico_analise_patrimonial", "/historico_analise_dmpl")
dmpl_html = dmpl_html.replace("/excluir_analise_patrimonial/", "/excluir_analise_dmpl/")
dmpl_html = dmpl_html.replace("/salvar_analise_patrimonial/", "/salvar_analise_dmpl/")
dmpl_html = dmpl_html.replace("/gerar_pdf_analise_patrimonial/", "/gerar_pdf_analise_dmpl/")
dmpl_html = dmpl_html.replace("/api/analise_patrimonial/", "/api/analise_dmpl/")

# 3.3 Nome da funcao de renderizacao (DVP usa 'render', DMPL usara 'render' tambem)
# A funcao 'render' no codigo da DVP ja faz a tabela e o grafico

# 3.4 Corrige a funcao exibirSelecionado para usar a nova rota
import re
# A funcao exibirSelecionado da DVP ja esta correta, so precisamos garantir que a rota mude
# (ja foi trocada no replace acima)

# 4. Salva o novo arquivo
with open("analise_dmpl.html", "w", encoding="utf-8") as f:
    f.write(dmpl_html)

print("OK: analise_dmpl.html reescrito com a estrutura da DVP!")
