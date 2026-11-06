import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_fix_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. FORÇAR A BARRA DE BOTOES COM ONCLICK E SEM NAVEGAÇÃO
top_bar_html = """
<div class="top-bar" style="display:flex; gap:10px; padding:10px; background: #f4f6f9; flex-wrap: wrap; align-items: center;">
    <a href="/" class="btn" style="background:#ff7f00; color:white; padding:8px 16px; border-radius:6px; text-decoration:none; font-weight:bold;">← Voltar</a>
    <button class="btn" onclick="exibirSelecionado()" style="background:#28a745; color:white; padding:8px 16px; border-radius:6px; border:none; cursor:pointer; font-weight:bold;">Exibir Selecionado</button>
    <button class="btn" onclick="excluirSelecionado()" style="background:#dc3545; color:white; padding:8px 16px; border-radius:6px; border:none; cursor:pointer; font-weight:bold;">Excluir Selecionado</button>
    <button class="btn" onclick="gerarPDFPanorama()" style="background:#0056b3; color:white; padding:8px 16px; border-radius:6px; border:none; cursor:pointer; font-weight:bold;">Gerar PDF</button>
    <button class="btn" id="btn-salvar" onclick="salvarPanorama()" style="background:#38a169; color:white; padding:8px 16px; border-radius:6px; border:none; cursor:pointer; font-weight:bold; display:none;">Confirmar e Salvar</button>
</div>
"""
html = re.sub(r'<div class="top-bar".*?</div>', top_bar_html, html, flags=re.DOTALL | re.IGNORECASE)

# 2. NOVO JAVASCRIPT BLINDADO
novo_js = """
// ===== JAVASCRIPT DEFINITIVO 2.0 - PANORAMA =====

function updateValueByLabel(labelTexts, newValue) {
    const format = (val) => {
        if (val === undefined || val === null) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };
    const formatted = format(newValue);
    
    // Varre os elementos folha (sem filhos)
    const elements = Array.from(document.querySelectorAll('div, span, p, h1, h2, h3, h4'));
    for (let el of elements) {
        if (el.children.length === 0) { 
            let text = el.innerText.trim().toLowerCase();
            // Verifica se o texto do elemento bate EXATAMENTE com um dos rótulos
            if (labelTexts.some(l => text === l.toLowerCase())) {
                let parent = el.parentElement;
                let updated = false;
                if (parent) {
                    // Acha qualquer elemento irmão que tenha R$ ou 0,0
                    let values = Array.from(parent.querySelectorAll('*')).filter(child => 
                        child !== el && child.children.length === 0 && (child.innerText.includes('R$') || child.innerText.includes('0,0'))
                    );
                    if (values.length > 0) {
                        values[0].innerText = formatted; 
                        updated = true;
                    }
                }
                if (!updated) {
                    let next = el.nextElementSibling;
                    if (next && (next.innerText.includes('R$') || next.innerText.includes('0,0'))) {
                        next.innerText = formatted;
                    }
                }
            }
        }
    }
}

async function carregarPanorama() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    let valor = (tipo === 'MES') ? document.getElementById('mes').value : (tipo === 'TRIMESTRE') ? document.getElementById('trimestre').value : "1";
    const periodo = ano + '-' + tipo + '-' + valor;
    
    const titulo = document.getElementById("periodo-titulo");
    if (titulo) titulo.innerText = (tipo === 'TRIMESTRE') ? valor + "º Trimestre de " + ano : (tipo === 'MES') ? "Mês " + valor + " de " + ano : "Exercício de " + ano;
    
    try {
        const response = await fetch(`/api/panorama/${periodo}`);
        const data = await response.json();
        
        if (data.erro === "faltando") { alert("Faltam peças: " + data.pecas.join(', ')); return; }
        if (data.erro || data.detail) { alert("Erro: " + (data.mensagem || data.detail)); return; }
        
        aplicarValores(data);
        
        const btnSalvar = document.getElementById("btn-salvar");
        if(btnSalvar) {
            btnSalvar.setAttribute("data-periodo", periodo);
            btnSalvar.style.display = "inline-block";
            btnSalvar.innerText = "Confirmar e Salvar";
            btnSalvar.disabled = false;
        }
    } catch (e) { 
        console.error("Erro", e); 
        alert("Erro de conexão.");
    }
}

function aplicarValores(data) {
    updateValueByLabel(['Caixa e Equivalente de Caixa (BP)', 'Caixa e Equivalentes'], data.caixa_bp);
    updateValueByLabel(['Ativo Total'], data.ativo_total);
    updateValueByLabel(['Passivo Total'], data.passivo_total);
    updateValueByLabel(['Patrimônio Líquido', 'Patrimonio Liquido'], data.patrimonio_liquido);
    updateValueByLabel(['Receitas Realizadas (BO)', 'Receitas Realizadas'], data.receita_realizada);
    updateValueByLabel(['Despesas Empenhadas (BO)', 'Despesas Empenhadas'], data.despesa_empenhada);
    updateValueByLabel(['Superávit Orçamentário', 'Déficit Orçamentário'], data.superavit_orcamentario);
    updateValueByLabel(['Superávit Patrimonial (DVP)', 'Superávit Patrimonial'], data.superavit_patrimonial);
    updateValueByLabel(['Superávit Financeiro (BP)', 'Superávit Financeiro'], data.superavit_financeiro);
}

async function salvarPanorama() {
    const btn = document.getElementById("btn-salvar");
    if (!btn) return;
    const periodo = btn.getAttribute("data-periodo");
    if (!periodo) { alert("Clique em 'Verificar' antes."); return; }
    
    btn.innerText = "Salvando..."; btn.disabled = true;
    try {
        const res = await fetch("/salvar_panorama/" + periodo, { method: "POST" });
        if(res.ok) {
            alert("Resultados salvos com sucesso!");
            carregarHistorico();
        } else {
            alert("Erro no servidor (" + res.status + ").");
        }
    } catch (e) { 
        alert("Erro de conexão."); 
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
            const list = document.getElementById('lista-historico');
            if(list) list.innerHTML = html;
        })
        .catch(e => console.error("Erro no historico", e));
}

async function exibirSelecionado() {
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    
    try {
        const res = await fetch(`/historico_panorama/${check.value}`);
        const data = await res.json();
        if (data.erro) { alert("Erro ao carregar histórico."); return; }
        
        // Remove o ?id=... da URL sem recarregar a página
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, null, window.location.pathname);
        }
        
        let payload = data.dados ? data.dados : data;
        if (typeof payload === 'string') {
            payload = JSON.parse(payload);
        }
        
        aplicarValores(payload); 
        window.scrollTo(0, 0);
    } catch(e) {
        alert("Erro de conexão ao exibir histórico.");
    }
}

async function excluirSelecionado() {
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    if (!confirm("Excluir este item do histórico?")) return;
    
    try {
        await fetch(`/excluir_panorama/${check.value}`, { method: 'DELETE' });
        carregarHistorico();
    } catch(e) {
        alert("Erro ao excluir.");
    }
}

function gerarPDFPanorama() {
    const check = document.querySelector('.check-historico:checked');
    if (!check) { alert("Selecione um item no histórico para gerar o PDF."); return; }
    window.open(`/gerar_pdf_panorama/${check.value}`, '_blank');
}

// Exporta pro escopo global
window.carregarPanorama = carregarPanorama;
window.salvarPanorama = salvarPanorama;
window.exibirSelecionado = exibirSelecionado;
window.excluirSelecionado = excluirSelecionado;
window.gerarPDFPanorama = gerarPDFPanorama;

document.addEventListener("DOMContentLoaded", () => {
    carregarHistorico();
});
"""

scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE))
for m in reversed(scripts):
    if 'carregarPanorama' in m.group(1):
        html = html[:m.start(1)] + novo_js + html[m.end(1):]
        break

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Frontend reescrito (v2.0).")
print("[OK] Botao 'Exibir' nao recarrega mais a pagina e os valores nao se cruzam.")
print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador: http://127.0.0.1:9994/panorama")
print("2. Aperte Ctrl + Shift + R (MUITO IMPORTANTE).")
print("3. Clique em Exibir Selecionado com um item marcado na lista.")
