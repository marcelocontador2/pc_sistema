import shutil

# 1. Backup do arquivo atual
shutil.copy("analise_dmpl.html", "analise_dmpl.html.bak_reset_final")

# 2. Le o arquivo da DVP (que esta funcionando 100%)
with open("analise_patrimonial.html", "r", encoding="utf-8") as f:
    html = f.read()

# 3. Faz as substituicoes cirurgicas
html = html.replace("Análise Patrimonial (DVP)", "Análise DMPL")
html = html.replace("Demonstração das Variações Patrimoniais (DVP)", "Demonstração das Mutações do Patrimônio Líquido (DMPL)")

# 3.1 Rotas
html = html.replace("/historico_analise_patrimonial", "/historico_analise_dmpl")
html = html.replace("/excluir_analise_patrimonial/", "/excluir_analise_dmpl/")
html = html.replace("/salvar_analise_patrimonial/", "/salvar_analise_dmpl/")
html = html.replace("/gerar_pdf_analise_patrimonial/", "/gerar_pdf_analise_dmpl/")
html = html.replace("/api/analise_patrimonial/", "/api/analise_dmpl/")

# 4. Salva o novo arquivo
with open("analise_dmpl.html", "w", encoding="utf-8") as f:
    f.write(html)

print("OK: analise_dmpl.html reconstruido com a estrutura da DVP!")
