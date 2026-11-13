import shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_rota_404")

# Corrige a rota antiga do SQLite para a rota nova do PostgreSQL
antigo = "fetch('/historico_composicao_rd/' + check.value)"
novo = "fetch('/historico_composicao_receitas_despesas/' + check.value)"

if antigo in s:
    s = s.replace(antigo, novo, 1)
    print("OK: Rota '/historico_composicao_rd/' corrigida para '/historico_composicao_receitas_despesas/'")
else:
    print("AVISO: Rota antiga nao encontrada.")

# Tambem corrige a rota de listagem inicial (se estiver usando a antiga)
s = s.replace("fetch('/historico_composicao_rd')", "fetch('/historico_composicao_receitas_despesas')")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
