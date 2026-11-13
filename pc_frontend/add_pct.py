import shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_add_pct")

# Adiciona a funcao pct antes da funcao renderTabela
funcao_pct = """
function pct(a, b) {
    if (!b || b === 0) return '-';
    const v = ((a - b) / Math.abs(b)) * 100;
    return (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
}

"""

if "function pct(" not in s:
    # Insere antes da funcao renderTabela
    ancora = "function renderTabela("
    if ancora in s:
        s = s.replace(ancora, funcao_pct + ancora, 1)
        print("OK: Funcao pct adicionada antes de renderTabela.")
    else:
        print("ERRO: funcao renderTabela nao encontrada para ancorar.")
else:
    print("AVISO: Funcao pct ja existe.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
