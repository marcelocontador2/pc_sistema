import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_carregar_final")

# Encontra a funcao carregar (sem async)
padrao = re.compile(r'function carregar\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """function carregar() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    const periodo = ano + '-' + tipo + '-' + val;

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

            // Preenche a tabela de Receitas
            const tbRec = document.getElementById('tbody-receitas');
            if (tbRec) {
                let html = '';
                for (const [key, val] of Object.entries(dados.receitas || {})) {
                    html += `<tr>
                        <td>${key}</td>
                        <td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                        <td style="text-align:right;">0,00</td>
                        <td style="text-align:right;">-</td>
                    </tr>`;
                }
                tbRec.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
            }

            // Preenche a tabela de Despesas
            const tbDesp = document.getElementById('tbody-despesas');
            if (tbDesp) {
                let html = '';
                for (const [key, val] of Object.entries(dados.despesas || {})) {
                    html += `<tr>
                        <td>${key}</td>
                        <td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                        <td style="text-align:right;">0,00</td>
                        <td style="text-align:right;">-</td>
                    </tr>`;
                }
                tbDesp.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
            }

            // Se houver grafico, atualiza
            if (typeof renderChart === 'function') {
                renderChart(dados);
            }
        })
        .catch(e => {
            alert("Erro ao carregar: " + e.message);
            console.error(e);
        });
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao carregar() reescrita com sucesso.")
else:
    print("ERRO: Funcao carregar() nao encontrada.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
