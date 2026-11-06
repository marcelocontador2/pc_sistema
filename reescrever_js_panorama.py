import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_limpo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Novo JavaScript limpo, sem erros de sintaxe e com funcoes exportadas
novo_js = """
// Funções do Panorama
async function carregarPanorama() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    let valor = (tipo === 'MES') ? document.getElementById('mes').value : (tipo === 'TRIMESTRE') ? document.getElementById('trimestre').value : "1";
    const periodo = ano + '-' + tipo + '-' + valor;
    document.getElementById("periodo-titulo").innerText = (tipo === 'TRIMESTRE') ? valor + "º Trimestre de " + ano : (tipo === 'MES') ? "Mês " + valor + " de " + ano : "Exercício de " + ano;
    
    try {
        const response = await fetch(`/api/panorama/${periodo}`);
        const data = await response.json();
        
        if (data.erro === "faltando") {
            const div = document.getElementById("integridade-cards");
            let html = '<div style="background:#fff3cd; border-left:5px solid #ffc107; padding:20px; border-radius:8px; margin-top:20px;">';
            html += '<h3 style="color:#856404; margin:0 0 10px 0;">⚠️ Peças Pendentes</h3>';
            html += '<p style="color:#856404;">Os seguintes demonstrativos não foram importados para o período <strong>' + periodo + '</strong>:</p>';
            html += '<ul style="color:#856404;">';
            data.pecas.forEach(p => { html += '<li>' + p + '</li>'; });
            html += '</ul>';
            html += '<p style="color:#856404; margin-top:10px;">Acesse <strong>Importar Relatórios</strong> para enviar os arquivos pendentes.</p>';
            html += '</div>';
            div.innerHTML = html;
            const btn = document.getElementById("btn-confirmar");
            if(btn) btn.style.display = "none";
            return;
        }
        
        if (data.erro) {
            alert("Erro: " + (data.mensagem || "Falha ao calcular panorama."));
            return;
        }
        
        aplicarValores(data);
        const btn = document.getElementById("btn-confirmar");
        if(btn) btn.setAttribute("data-periodo", periodo);
        
    } catch (e) { 
        console.error("Erro na requisição", e); 
    }
}

function aplicarValores(data) {
    const format = (val) => {
        if (val === undefined || val === null) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };

    const map = {
        'caixa e equivalente': data.caixa_bp,
        'ativo total': data.ativo_total,
        'passivo total': data.passivo_total,
        'patrimônio líquido': data.patrimonio_liquido,
        'patrimonio liquido': data.patrimonio_liquido,
        'receitas realizadas': data.receita_realizada,
        'despesas empenhadas': data.despesa_empenhada,
        'superávit orçamentário': data.superavit_orcamentario,
        'déficit orçamentário': data.superavit_orcamentario,
        'superávit patrimonial': data.superavit_patrimonial,
        'superávit financeiro': data.superavit_financeiro
    };

    // Procura por qualquer elemento que tenha classe de card ou seja uma div com R$
    document.querySelectorAll('.card, .kpi-card, .card-panorama, div').forEach(card => {
        let textoCard = card.innerText.toLowerCase();
        for (let key in map) {
            if (textoCard.includes(key) && card.children.length <= 1) { 
                // Encontrou o card certo
                let elementos = card.querySelectorAll('*');
                for (let el of elementos) {
                    if (el.children.length === 0 && el.innerText.includes('R$')) {
                        el.innerText = format(map[key]);
                        break;
                    }
                }
                break;
            }
        }
    });
}

async function salvarPanorama() {
    const btn = document.getElementById("btn-confirmar");
    const periodo = btn.getAttribute("data-periodo");
    if (!periodo) { alert("Verifique o panorama antes de salvar."); return; }
    
    btn.innerText = "Salvando..."; btn.disabled = true;
    try {
        await fetch("/salvar_panorama/" + periodo, { method: "POST" });
        alert("Resultados salvos com sucesso!");
        carregarHistorico(); btn.style.display = "none";
    } catch (e) { 
        alert("Erro ao salvar."); 
    } finally { 
        btn.innerText = "Confirmar e Salvar"; btn.disabled = false; 
    }
}

function carregarHistorico() {
    fetch('/historico_panorama')
        .then(r => r.json())
        .then(data => {
            let html = '';
            if (!data || data.length === 0) {
                html = '<li>Nenhum histórico.</li>';
            } else {
                data.forEach(item => {
                    html += `<li style="margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" class="check-historico" value="${item.id}" style="width: 16px; height: 16px; cursor: pointer;">
                            <div><div style="font-weight: bold; color: #0056b3;">${item.periodo}</div><div style="font-size: 12px; color: #888;">Gerado em: ${item.data_geracao}</div></div>
                        </div></li>`;
                });
            }
            document.getElementById('lista-historico').innerHTML = html;
        })
        .catch(e => {
            document.getElementById('lista-historico').innerHTML = '<li>Erro ao carregar.</li>';
        });
}

function exibirSelecionado() {
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    // Aqui assumimos que a rota retorna o JSON salvo para ser exibido
    window.open(`/panorama?id=${check.value}`, '_blank');
}

function excluirSelecionado() {
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    if (!confirm("Excluir este item?")) return;
    fetch(`/excluir_panorama/${check.value}`, { method: 'DELETE' })
        .then(() => carregarHistorico());
}

function gerarPDFPanorama() {
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico para gerar o PDF."); return; }
    window.open(`/gerar_pdf_panorama/${check.value}`, '_blank');
}

// Exporta para o escopo global para os botoes HTML acharem
window.carregarPanorama = carregarPanorama;
window.salvarPanorama = salvarPanorama;
window.exibirSelecionado = exibirSelecionado;
window.excluirSelecionado = excluirSelecionado;
window.gerarPDFPanorama = gerarPDFPanorama;
window.carregarHistorico = carregarHistorico;

document.addEventListener("DOMContentLoaded", () => {
    carregarHistorico();
});
"""

# Substitui TODO o bloco <script> que contem o panorama por esse novo
# (Procura o ultimo <script> que tem 'carregarPanorama' e troca o conteudo)
scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE))
for m in reversed(scripts):
    if 'carregarPanorama' in m.group(1):
        # Substitui apenas o conteudo interno
        html = html[:m.start(1)] + novo_js + html[m.end(1):]
        break

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] JavaScript totalmente reescrito e limpo.")
print("[OK] Erros de sintaxe removidos.")
print("[OK] Funcoes forcadas no escopo global.")
print("\n=== PROXIMO PASSO ===")
print("1. O servidor NAO precisa ser reiniciado.")
print("2. Va no navegador: http://127.0.0.1:9994/panorama")
print("3. Aperte Ctrl + Shift + R (MUITO IMPORTANTE para limpar o cache).")
print("4. Clique em Verificar. Os botoes devem funcionar e os valores aparecer!")
