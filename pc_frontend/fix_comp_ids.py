import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_ids")

# 1) Ajusta os IDs das tabelas no HTML (a DMPL usa 'tab', a Composicao precisa de 'tbody-receitas' e 'tbody-despesas')
# Primeiro, verifica se ja existem esses IDs
if 'id="tbody-receitas"' not in s and 'id="tbody-despesas"' not in s:
    # Substitui a tabela unica por duas tabelas (receitas e despesas)
    # Encontra a tabela atual e substitui
    antigo_tab = re.search(r'<table[^>]*id="tab"[^>]*>.*?</table>', s, re.DOTALL)
    if antigo_tab:
        nova_estrutura = '''
        <h3>Receitas — comparativo (R$ mil)</h3>
        <table class="tabela-dados">
            <thead><tr><th>Conta</th><th>Período Atual</th><th>Período Anterior</th><th>Var. (%)</th></tr></thead>
            <tbody id="tbody-receitas"><tr><td colspan="4" style="text-align:center">Clique em Verificar</td></tr></tbody>
        </table>
        
        <h3 style="margin-top: 30px;">Despesas — comparativo (R$ mil)</h3>
        <table class="tabela-dados">
            <thead><tr><th>Conta</th><th>Período Atual</th><th>Período Anterior</th><th>Var. (%)</th></tr></thead>
            <tbody id="tbody-despesas"><tr><td colspan="4" style="text-align:center">Clique em Verificar</td></tr></tbody>
        </table>
        '''
        s = s[:antigo_tab.start()] + nova_estrutura + s[antigo_tab.end():]
        print("OK: Tabelas de Receitas e Despesas criadas no HTML.")

# 2) Corrige a funcao carregar() (que pode estar como 'function carregar()')
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
                        <td style="text-align:right;">-</td>
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
                        <td style="text-align:right;">-</td>
                        <td style="text-align:right;">-</td>
                    </tr>`;
                }
                tbDesp.innerHTML = html || '<tr><td colspan="4" style="text-align:center">Nenhum dado.</td></tr>';
            }
        })
        .catch(e => {
            alert("Erro ao carregar: " + e.message);
            console.error(e);
        });
}
"""
    s = s[:match.start()] + nova_func + s[match.end():]
    print("OK: Funcao carregar() reescrita para a Composicao.")
else:
    print("AVISO: Funcao carregar() nao encontrada (pode estar com async).")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
