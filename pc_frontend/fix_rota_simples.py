import shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_rota_final")

# Troca a rota antiga do SQLite pela rota nova do PostgreSQL
antigo = "fetch('/historico_composicao_rd/' + check.value)"
novo = "fetch('/historico_composicao_receitas_despesas/' + check.value)"

qtd = s.count(antigo)
if qtd > 0:
    s = s.replace(antigo, novo)
    print(f"OK: Rota antiga substituída em {qtd} lugar(es).")
else:
    print("AVISO: Rota antiga não encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
