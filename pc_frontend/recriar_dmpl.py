import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_limpeza_total")

# 1. Limpa TODOS os scripts antigos que podem estar quebrando a pagina
# Remove qualquer tag <script>...</script> para recomecar do zero
s = re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.DOTALL | re.IGNORECASE)

# 2. Adiciona o novo script limpo antes do fechamento do </body>
novo_script = '''
<script>
// Funcao para carregar o historico (roda assim que a pagina abre)
function carregarHistorico() {
    fetch('/historico_analise_dmpl')
        .then(r => r.json())
        .then(data => {
            const lista = document.getElementById('historico-lista');
            if (!lista) return;
            if (!data || data.length === 0) { lista.innerHTML = '<div style="padding:10px; color:#777;">Nenhum histórico.</div>'; return; }
            
            let html = '';
            data.forEach(item => {
                html += `<div class="hist-item" style="margin-bottom:8px;">
                    <input type="checkbox" value="${item.id}" class="check-hist" style="margin-right:8px;">
                    <span style="font-weight:bold; color:#0056b3;">${item.periodo}</span><br>
                    <span style="font-size:11px; color:#888;">Gerado em: ${item.data_geracao}</span>
                </div>`;
            });
            lista.innerHTML = html;
        })
        .catch(e => console.error("Erro no historico:", e));
}

// Funcao para exibir os dados selecionados
function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked");
    if (!check) { alert("Selecione um item no histórico primeiro."); return; }
    
    const id = check.value;
    const tbody = document.querySelector('#tab tbody');
    if(tbody) tbody.innerHTML = '<tr><td colspan="2">Carregando dados...</td></tr>';

    fetch('/historico_analise_dmpl/' + id)
        .then(r => r.json())
        .then(item => {
            if (!item || item.erro) { alert("Histórico não encontrado."); return; }
            
            let dados = item.dados;
            if (typeof dados === 'string') {
                try { dados = JSON.parse(dados); } catch(e) { dados = []; }
            }
            
            const d = dados?.dados || dados || [];
            
            let html = '';
            d.forEach(linha => {
                if (!Array.isArray(linha) || linha.length < 2) return;
                const nome = (linha[0] || '').trim();
                if(!nome || nome.includes('COFEN/BR') || nome.includes('CNPJ:')) return;
                
                const valorStr = (linha[1] || '0').trim();
                let valor = parseFloat(valorStr.replace(/\\./g, '').replace(',', '.')) || 0;
                let valorFormatado = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                
                html += `<tr>
                    <td style="text-align:left;">${nome}</td>
                    <td style="text-align:right;">${valorFormatado}</td>
                </tr>`;
            });

            if(tbody) tbody.innerHTML = html || '<tr><td colspan="2" style="text-align:center;">Nenhum dado encontrado no JSON.</td></tr>';
        })
        .catch(e => {
            console.error(e);
            if(tbody) tbody.innerHTML = '<tr><td colspan="2" style="text-align:center; color:red;">Erro ao carregar os dados.</td></tr>';
        });
}

// Quando a pagina carregar, inicia o historico
document.addEventListener("DOMContentLoaded", () => {
    carregarHistorico();
    
    // Garante que o botao Exibir vai funcionar
    const btnExibir = document.querySelector('button.btn-exibir') || document.querySelector('button[onclick*="exibirSelecionado"]') || document.querySelector('.btn-salvar');
    if(btnExibir) {
        btnExibir.setAttribute("onclick", "exibirSelecionado()");
    }
});
</script>
'''

if "</body>" in s:
    s = s.replace("</body>", novo_script + "\n</body>")
else:
    s += novo_script

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

print("OK: Arquivo analise_dmpl.html recriado com JavaScript limpo!")
