import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_ids_reais")

# 1) Corrige a funcao carregar() para usar os IDs REAIS (tipo, val)
padrao = re.compile(r'(async\s+)?function carregar\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """function carregar() {
    const tipo = document.getElementById('tipo').value;
    const val = document.getElementById('val').value;
    const periodo = '2026-' + tipo + '-' + val;

    fetch('/api/composicao_receitas_despesas/' + periodo)
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        })
        .then(dados => {
            if (dados.erro === "faltando") {
                alert("Arquivos faltando: " + dados.pecas.join(', '));
                return;
            }
            if (dados.erro) {
                alert("Erro: " + dados.mensagem);
                return;
            }
            // Chama a funcao render() que ja existe no arquivo para preencher as tabelas
            if (typeof render === 'function') {
                render(dados);
            } else {
                // Fallback: preenche as tabelas se existirem
                const tbRec = document.querySelector('table tbody');
                if (tbRec) {
                    let html = '';
                    for (const [key, val] of Object.entries(dados.receitas || {})) {
                        html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
                    }
                    tbRec.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
                }
            }
        })
        .catch(e => {
            alert("Erro ao carregar: " + e.message);
            console.error(e);
        });
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao carregar() corrigida com IDs reais e chamada ao render().")
else:
    print("AVISO: Funcao carregar() nao encontrada.")

# 2) Garante que o carregamento inicial do historico seja chamado
if "carregarHistorico()" not in s:
    s = s.replace("document.addEventListener('DOMContentLoaded', carregarHistorico);", "")
    s = s.replace("</script>", "document.addEventListener('DOMContentLoaded', carregarHistorico);\n</script>")
    print("OK: Chamada inicial do historico adicionada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
