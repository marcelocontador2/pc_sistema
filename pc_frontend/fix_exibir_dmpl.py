import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_exibir_dmpl")

# Encontra a função exibirSelecionado inteira (do inicio ao fechamento da chave)
padrao = re.compile(
    r'function exibirSelecionado\(\)\s*\{.*?\n\s*\}',
    re.DOTALL
)

# Nova função corrigida (async, chamando a rota certa e lendo o campo certo)
nova_funcao = '''async function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked") || document.querySelector(".check-historico:checked");
    if (!check) { alert("Selecione um item no histórico."); return; }
    const idProcurado = check.value;

    try {
        // Chama a rota de ID que criamos no backend
        const r = await fetch('/historico_analise_dmpl/' + idProcurado);
        if (!r.ok) throw new Error("HTTP " + r.status);
        const item = await r.json();
        
        if (!item || item.erro) { alert("Histórico não encontrado."); return; }

        // O backend envia os dados dentro da propriedade "dados"
        let dados = item.dados;
        if (typeof dados === 'string') {
            try { dados = JSON.parse(dados); } catch(e) { dados = null; }
        }
        
        // Se o JSON salvo tiver uma propriedade "dados" interna, usa ela
        const d = dados?.dados || dados || [];

        // Atualiza o cabecalho da tabela para o padrao DMPL
        const thead = document.querySelector('#tab thead tr');
        if (thead) {
            thead.innerHTML = '<th style="text-align:left;">Especificação</th><th style="text-align:right;">Valor Total (R$)</th>';
        }

        let html = '';
        let labels = [];
        let dadosAtual = [];

        d.forEach((linha, index) => {
            if (!Array.isArray(linha) || linha.length < 9) return;
            
            const nome = (linha[0] || '').trim();
            const valorTotalStr = (linha[8] || '').trim();
            
            if (!nome || nome === 'COFEN/BR' || nome === 'Conselho Federal de Enfermagem' || nome.startsWith('CNPJ:')) return;
            
            // Formata o valor
            let valorTotal = parseFloat(valorTotalStr.replace(/\\./g, '').replace(',', '.')) || 0;
            let valorFormatado = valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            
            html += `<tr>
                <td style="text-align:left;">${nome}</td>
                <td style="text-align:right;">${valorFormatado}</td>
            </tr>`;
            
            labels.push(nome);
            dadosAtual.push(valorTotal);
        });

        const tbody = document.querySelector('#tab tbody');
        if (tbody) tbody.innerHTML = html || '<tr><td colspan="2">Nenhum dado encontrado.</td></tr>';

    } catch (e) {
        console.error("Erro ao exibir DMPL:", e);
        alert("Erro ao carregar os dados do histórico.");
    }
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao exibirSelecionado reescrita com sucesso!")
else:
    print("AVISO: Nao foi possivel substituir a funcao. Verifique manualmente no arquivo.")
