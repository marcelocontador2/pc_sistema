import shutil

# 1. Backup do arquivo atual
shutil.copy("composicao_receitas_despesas.html", "composicao_receitas_despesas.html.bak_regra")

# 2. Le o arquivo da DMPL (que funciona)
with open("analise_dmpl.html", "r", encoding="utf-8") as f:
    html = f.read()

# 3. Faz as substituicoes para a Composicao
html = html.replace("Análise DMPL", "Composição de Receitas e Despesas")
html = html.replace("Demonstração das Mutações do Patrimônio Líquido (DMPL)", "Receitas e Despesas Comparativas")

# 3.1 Rotas da API
html = html.replace("/historico_analise_dmpl", "/historico_composicao_receitas_despesas")
html = html.replace("/salvar_analise_dmpl/", "/salvar_composicao_receitas_despesas/")
html = html.replace("/excluir_analise_dmpl/", "/excluir_composicao_receitas_despesas/")
html = html.replace("/gerar_pdf_analise_dmpl/", "/gerar_pdf_composicao_receitas_despesas/")
html = html.replace("/api/analise_dmpl/", "/api/composicao_receitas_despesas/")

# 4. Ajusta a funcao exibirSelecionado para a Composicao
import re
padrao = re.compile(r'async function exibirSelecionado\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match = padrao.search(html)

if match:
    nova_func = """async function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked") || document.querySelector(".check-historico:checked");
    if (!check) { alert("Selecione um item no histórico."); return; }
    const idProcurado = check.value;

    try {
        const r = await fetch('/historico_composicao_receitas_despesas');
        if (!r.ok) throw new Error("HTTP " + r.status);
        const lista = await r.json();
        const item = lista.find(i => String(i.id) === String(idProcurado));
        if (!item) { alert("Histórico não encontrado."); return; }

        let dados = item.resultado_json;
        if (typeof dados === 'string') {
            try { dados = JSON.parse(dados); } catch(e) { dados = null; }
        }
        
        // Pega os dados do periodo atual
        const d = dados?.atual || dados || {};

        // Renderiza as tabelas de Receitas e Despesas
        const tbRec = document.getElementById('tbody-receitas');
        const tbDesp = document.getElementById('tbody-despesas');

        if (tbRec && d.receitas) {
            let html = '';
            for (const [key, val] of Object.entries(d.receitas)) {
                html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
            }
            tbRec.innerHTML = html;
        }
        if (tbDesp && d.despesas) {
            let html = '';
            for (const [key, val] of Object.entries(d.despesas)) {
                html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
            }
            tbDesp.innerHTML = html;
        }
    } catch (e) {
        alert("Erro ao carregar o histórico: " + e.message);
        console.error(e);
    }
}
"""
    html = html[:match.start()] + nova_func + html[match.end():]
    print("OK: Funcao exibirSelecionado reescrita para a Composicao.")

# 5. Ajusta a funcao carregar() para a Composicao
padrao2 = re.compile(r'async function carregar\(\)\s*\{.*?(?=\n\s*function|\Z)', re.DOTALL)
match2 = padrao2.search(html)

if match2:
    nova_func2 = """async function carregar() {
    const ano = document.getElementById('ano_atual').value;
    const tipo = document.getElementById('tipo_atual').value;
    const val = document.getElementById('val_atual').value;
    const periodo = ano + '-' + tipo + '-' + val;

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

        // Preenche as tabelas
        const tbRec = document.getElementById('tbody-receitas');
        const tbDesp = document.getElementById('tbody-despesas');

        if (tbRec && dados.receitas) {
            let html = '';
            for (const [key, val] of Object.entries(dados.receitas)) {
                html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
            }
            tbRec.innerHTML = html;
        }
        if (tbDesp && dados.despesas) {
            let html = '';
            for (const [key, val] of Object.entries(dados.despesas)) {
                html += `<tr><td>${key}</td><td style="text-align:right;">${(val/1000).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td style="text-align:right;">-</td><td style="text-align:right;">-</td></tr>`;
            }
            tbDesp.innerHTML = html;
        }
    } catch (e) {
        alert("Erro ao carregar: " + e.message);
        console.error(e);
    }
}
"""
    html = html[:match2.start()] + nova_func2 + html[match2.end():]
    print("OK: Funcao carregar() reescrita para a Composicao.")

# 6. Salva o arquivo
with open("composicao_receitas_despesas.html", "w", encoding="utf-8") as f:
    f.write(html)

print("OK: composicao_receitas_despesas.html reescrito com a regra de negocio correta!")
