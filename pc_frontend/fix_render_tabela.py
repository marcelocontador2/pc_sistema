import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_render_tabela_fix")

# Corrige a funcao renderTabela para usar as funcoes que existem no arquivo
padrao = re.compile(r'function renderTabela\([^)]*\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """function renderTabela(id, at, ant){
  const tb = document.querySelector('#'+id+' tbody');
  if (!tb) return;
  let html = '';
  Object.keys(at).forEach(function(k) {
    const va = at[k] || 0, vb = ant[k] || 0;
    // Usa a funcao pct (que existe no arquivo) em vez de pctVar
    const v = pct(va, vb);
    const cls = v.startsWith('-') ? 'neg' : 'pos';
    // Usa fmtV (que existe) para formatar os valores
    html += '<tr><td>' + k + '</td><td>' + fmtV(va) + '</td><td>' + fmtV(vb) + '</td><td class="' + cls + '">' + v + '</td></tr>';
  });
  tb.innerHTML = html;
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao renderTabela corrigida para usar a funcao pct (que existe).")
else:
    print("ERRO: Funcao renderTabela nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
