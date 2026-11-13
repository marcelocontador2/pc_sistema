import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_final")

# 1) Encontra a funcao 'carregar' (que e chamada pelo botao Verificar)
# O botao no HTML tem onclick="carregar()"
# Vamos reescrever a funcao carregar() inteira
padrao = re.compile(r'async function carregar\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(s)

if match:
    nova_func = """async function carregar() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    const periodo = `${ano}-${tipo}-${val}`;

    try {
        const r = await fetch('/api/composicao_receitas_despesas/' + periodo);
        if (!r.ok) throw new Error("HTTP " + r.status);
        const dados = await r.json();

        if (dados.erro === "faltando") {
            alert("Arquivos faltando: " + dados.pecas.join(', '));
            return;
        }
        if (dados.erro) {
            alert("Erro: " + dados.mensagem);
            return;
        }

        // Renderiza as tabelas com os dados recebidos
        if (typeof renderTabela === 'function') {
            renderTabela(dados);
        } else {
            // Fallback: preenche manualmente
            const tbRec = document.getElementById('tbody-receitas');
            const tbDesp = document.getElementById('tbody-despesas');
            
            if (tbRec) {
                let html = '';
                for (const [key, val] of Object.entries(dados.receitas || {})) {
                    html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">0,00</td><td style="text-align:right;">-</td></tr>`;
                }
                tbRec.innerHTML = html;
            }
            if (tbDesp) {
                let html = '';
                for (const [key, val] of Object.entries(dados.despesas || {})) {
                    html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">0,00</td><td style="text-align:right;">-</td></tr>`;
                }
                tbDesp.innerHTML = html;
            }
        }
    } catch (e) {
        alert("Erro ao carregar: " + e.message);
        console.error(e);
    }
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao carregar() reescrita com fetch correto e fallback.")
else:
    print("AVISO: Funcao carregar() nao encontrada. Tentando substituir por outro nome...")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
