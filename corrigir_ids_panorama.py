import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_ids_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. INJETAR IDs ÚNICOS NOS VALORES DO HTML
# Isso garante que o JS sempre ache o lugar certo, sem cruzamentos
def injetar_id(html_content, label, id_novo):
    # Procura o texto do label, e o próximo "R$ ... mi" depois dele
    padrao = re.compile(r'(' + re.escape(label) + r'.*?)(R\$ ?[\d\.,]+(?: mi)?)', re.DOTALL | re.IGNORECASE)
    def repl(m):
        # Evita duplicar ID se já existir
        if f'id="{id_novo}"' in m.group(0):
            return m.group(0)
        return m.group(1) + f'<span id="{id_novo}">' + m.group(2) + '</span>'
    return padrao.sub(repl, html_content, count=1)

html = injetar_id(html, 'Caixa e Equivalente de Caixa (BP)', 'val-caixa')
html = injetar_id(html, 'Ativo Total', 'val-ativo')
html = injetar_id(html, 'Passivo Total', 'val-passivo')
html = injetar_id(html, 'Patrimônio Líquido', 'val-pl')
html = injetar_id(html, 'Receitas Realizadas (BO)', 'val-receitas')
html = injetar_id(html, 'Despesas Empenhadas (BO)', 'val-despesas')
html = injetar_id(html, 'Superávit Orçamentário', 'val-superavit-orc')
html = injetar_id(html, 'Superávit Patrimonial (DVP)', 'val-superavit-pat')
html = injetar_id(html, 'Superávit Financeiro (BP)', 'val-superavit-fin')

# 2. SUBSTITUIR AS FUNÇÕES DO JAVASCRIPT
novo_js = """
// ===== JAVASCRIPT DEFINITIVO 3.0 - PANORAMA =====

function aplicarValores(data) {
    // Prepara os dados (pode vir da API ao vivo ou do Histórico salvo)
    let d = data;
    if (data.dados) d = data.dados; // Se for do histórico
    if (typeof d === 'string') d = JSON.parse(d); 
    if (d.dados) d = d.dados; // Se estiver duplamente embrulhado

    const format = (val) => {
        if (val === undefined || val === null || isNaN(val)) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };

    const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = format(val);
    };

    setVal('val-caixa', d.caixa_bp || d.caixa);
    setVal('val-ativo', d.ativo_total);
    setVal('val-passivo', d.passivo_total);
    setVal('val-pl', d.patrimonio_liquido || d.patrimonio);
    setVal('val-receitas', d.receita_realizada || d.receitas_realizadas);
    setVal('val-despesas', d.despesa_empenhada || d.despesas_empenhadas);
    setVal('val-superavit-orc', d.superavit_orcamentario !== undefined ? d.superavit_orcamentario : d.superavit_orc);
    setVal('val-superavit-pat', d.superavit_patrimonial);
    setVal('val-superavit-fin', d.superavit_financeiro);
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
        
        // Limpa a URL
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, null, window.location.pathname);
        }
        
        aplicarValores(data); 
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

print("[OK] IDs exclusivos injetados nos cards com sucesso.")
print("[OK] JavaScript v3.0 (aplicarValores agora e cirurgico e a prova de cruzamentos).")
print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador: http://127.0.0.1:9994/panorama")
print("2. Aperte Ctrl + Shift + R (MUITO IMPORTANTE).")
print("3. Clique em Verificar e depois em Exibir.")
