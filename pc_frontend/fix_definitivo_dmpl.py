import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_definitivo")

# 1. Substitui o botao antigo por um botao com ID (para nao depender de onclick global)
s = s.replace('<button class="btn btn-salvar" onclick="exibirSelecionado()">Exibir</button>', 
              '<button class="btn btn-salvar" id="btn-exibir">Exibir</button>')

# 2. Substitui a funcao exibirSelecionado inteira por uma versao limpa e assincrona
padrao_funcao = re.compile(r'function exibirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)

nova_funcao = '''async function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked");
    if (!check) { alert("Selecione um item no histórico."); return; }
    
    const idProcurado = check.value;
    const btn = document.getElementById('btn-exibir');
    if(btn) { btn.disabled = true; btn.innerText = 'Carregando...'; }

    try {
        const response = await fetch('/historico_analise_dmpl/' + idProcurado);
        if (!response.ok) throw new Error("Erro HTTP: " + response.status);
        
        const item = await response.json();
        if (!item || item.erro) { alert("Histórico não encontrado."); return; }

        let dados = item.dados;
        if (typeof dados === 'string') {
            try { dados = JSON.parse(dados); } catch(e) { dados = []; }
        }
        
        const d = dados?.dados || dados || [];
        const tbody = document.querySelector('#tab tbody');
        if(!tbody) return;

        let html = '';
        d.forEach(linha => {
            if (!Array.isArray(linha) || linha.length < 2) return;
            const nome = (linha[0] || '').trim();
            const valorStr = (linha[1] || '0').trim(); // Pega o segundo campo (valor)
            
            if(!nome || nome.includes('COFEN/BR') || nome.includes('CNPJ:')) return;
            
            let valor = parseFloat(valorStr.replace(/\\./g, '').replace(',', '.')) || 0;
            let valorFormatado = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            
            html += `<tr>
                <td style="text-align:left;">${nome}</td>
                <td style="text-align:right;">${valorFormatado}</td>
            </tr>`;
        });

        tbody.innerHTML = html || '<tr><td colspan="2">Nenhum dado encontrado.</td></tr>';

    } catch (e) {
        console.error(e);
        alert("Erro ao carregar os dados.");
    } finally {
        if(btn) { btn.disabled = false; btn.innerText = 'Exibir'; }
    }
}

// Adiciona o event listener no final do body
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById('btn-exibir');
    if(btn) btn.addEventListener('click', exibirSelecionado);
});
'''

nova_s, n = padrao_funcao.subn(nova_funcao, s)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Funcao e botao corrigidos com sucesso!")
else:
    print("AVISO: Nao foi possivel substituir a funcao. O HTML pode estar com outro formato.")
