import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_rotas")

# 1) Corrige as rotas do frontend para as rotas reais do backend
s = s.replace("/historico_composicao_rd/", "/historico_composicao_receitas_despesas")
s = s.replace("/historico_composicao_rd", "/historico_composicao_receitas_despesas")
s = s.replace("/api/composicao_receitas_despesas/", "/api/composicao_receitas_despesas/") # ja esta correto
s = s.replace("/salvar_composicao_receitas_despesas/", "/salvar_composicao_receitas_despesas/")
s = s.replace("/excluir_composicao_receitas_despesas/", "/excluir_composicao_receitas_despesas/")
s = s.replace("/gerar_pdf_composicao_receitas_despesas/", "/gerar_pdf_composicao_receitas_despesas/")

print("OK: Rotas do frontend corrigidas.")

# 2) Garante que a funcao de carregar historico use o ID correto
# (a funcao pode estar usando um campo diferente)
padrao = re.compile(r'function carregarHistorico\(\)\s*\{.*?\n\s*\}', re.DOTALL)
match = padrao.search(s)
if match:
    print("OK: Funcao carregarHistorico encontrada (verificando chamada)...")
    # Verifica se ela chama a rota correta
    if '/historico_composicao_receitas_despesas' not in match.group(0):
        print("AVISO: Funcao carregarHistorico nao chama a rota correta.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
