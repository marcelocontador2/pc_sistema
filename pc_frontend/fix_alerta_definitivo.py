import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Remove a funcao carregar() antiga inteira
padrao = re.compile(r'function carregar\(\)\s*\{.*?\n\}', re.DOTALL)
js = padrao.sub('', js)

# Adiciona a nova funcao carregar() no final do arquivo
nova_funcao = '''
async function carregar() {
    const ano = document.getElementById('ano') ? document.getElementById('ano').value : '2026';
    const tipo = document.getElementById('tipo') ? document.getElementById('tipo').value : 'TRIMESTRE';
    const periodo = document.getElementById('periodo') ? document.getElementById('periodo').value : '3';
    
    const periodoFormatado = `${ano}-${tipo.toUpperCase()}-${periodo}`;
    
    const tbody = document.querySelector('#tab tbody');
    const thead = document.querySelector('#tab thead tr');
    
    if(thead) {
        thead.innerHTML = '<th style="text-align:left;">Conta</th><th style="text-align:right;">Valor (R$)</th><th style="text-align:right;">% do Total</th>';
    }
    if(tbody) tbody.innerHTML = '<tr><td colspan="3">Verificando dados do CSV...</td></tr>';

    try {
        const response = await fetch('/api/analise_dmpl/' + periodoFormatado);
        
        // Se o servidor respondeu com erro (404, 500, etc)
        if (!response.ok) {
            let mensagemErro = "Erro desconhecido.";
            try {
                const erroJson = await response.json();
                mensagemErro = erroJson.mensagem || mensagemErro;
            } catch (e) {
                // Se nao for JSON, usa o status
                mensagemErro = "Erro HTTP " + response.status;
            }
            throw new Error(mensagemErro);
        }

        const retorno = await response.json();
        
        // Caso o backend retorne 200 OK mas com {erro: true}
        if (retorno && retorno.erro) {
            throw new Error(retorno.mensagem || "Nenhum dado para este periodo.");
        }

        let dados = retorno.dados || retorno;
        if (typeof dados === 'string') {
            try { dados = JSON.parse(dados); } catch(e) { dados = []; }
        }
        
        renderizarDados(dados);

    } catch (error) {
        console.error(error);
        // AQUI ESTA O ALERTA
        alert("Aviso: " + error.message);
        
        if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';
        
        if (window._chartDMPL) {
            window._chartDMPL.destroy();
            window._chartDMPL = null;
        }
    }
}
'''

js += nova_funcao

with open(path, "w", encoding="utf-8") as f:
    f.write(js)
print("OK: Funcao carregar() reescrita do zero com async/await e leitura de erro 404!")
