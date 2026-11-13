import re
import shutil

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_fix_conferencia_style")

# 1. Devolve o onclick no botao
s = s.replace('<button class="btn btn-salvar" id="btn-exibir">Exibir</button>', 
              '<button class="btn btn-salvar" onclick="exibirSelecionado()">Exibir</button>')

# 2. Substitui a funcao async inteira por uma versao com .then() (igual a conferencia)
padrao = re.compile(r'(async\s+)?function exibirSelecionado\(\)\s*\{.*?\n\s*\}', re.DOTALL)

nova_funcao = '''function exibirSelecionado() {
    const check = document.querySelector(".check-hist:checked");
    if (!check) { alert("Selecione um item no histórico."); return; }
    
    const idProcurado = check.value;
    
    fetch('/historico_analise_dmpl/' + idProcurado)
        .then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        })
        .then(item => {
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
                const valorStr = (linha[1] || '0').trim();
                
                if(!nome || nome.includes('COFEN/BR') || nome.includes('CNPJ:')) return;
                
                let valor = parseFloat(valorStr.replace(/\\./g, '').replace(',', '.')) || 0;
                let valorFormatado = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                
                html += `<tr>
                    <td style="text-align:left;">${nome}</td>
                    <td style="text-align:right;">${valorFormatado}</td>
                </tr>`;
            });

            tbody.innerHTML = html || '<tr><td colspan="2">Nenhum dado encontrado.</td></tr>';
        })
        .catch(e => {
            console.error(e);
            alert("Erro ao carregar os dados do histórico.");
        });
}'''

nova_s, n = padrao.subn(nova_funcao, s)

if n > 0:
    # Limpa qualquer addEventListener antigo que possa ter ficado
    nova_s = re.sub(r'document\.addEventListener\("DOMContentLoaded".*?\}\);\s*', '', nova_s, flags=re.DOTALL)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_s)
    print("OK: Tela DMPL padronizada igual a Conferencia (onclick + .then) e limpa!")
else:
    print("AVISO: Funcao nao encontrada para substituir.")
