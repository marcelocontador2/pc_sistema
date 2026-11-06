import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_limpeza_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Garantir que os botões tenham IDs limpos e remover onclicks antigos
def clean_and_add_id(html, texto_botao, id_novo):
    padrao = re.compile(r'<button([^>]*)>(.*?' + texto_botao + r'.*?)</button>', re.IGNORECASE | re.DOTALL)
    def repl(m):
        attrs = m.group(1)
        attrs = re.sub(r'onclick="[^"]*"', '', attrs) # Remove onclick antigo
        if 'id=' not in attrs:
            attrs += f' id="{id_novo}"'
        return f'<button{attrs}{m.group(2)}</button>'
    return padrao.sub(repl, html)

html = clean_and_add_id(html, 'Verificar', 'btn-verificar')
html = clean_and_add_id(html, 'Gerar PDF', 'btn-pdf')
html = clean_and_add_id(html, 'Confirmar e Salvar', 'btn-salvar')
html = clean_and_add_id(html, 'Exibir Selecionado', 'btn-exibir')
html = clean_and_add_id(html, 'Excluir Selecionado', 'btn-excluir')

# 2. Substituir TODO o bloco <script> por um código único e limpo
novo_js = """
// ===== JAVASCRIPT LIMPO DO PANORAMA =====

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
        
        if (data.erro === "faltando") {
            alert("Faltam peças para este período: " + data.pecas.join(', '));
            return;
        }
        if (data.erro || data.detail) {
            alert("Erro: " + (data.mensagem || data.detail || "Falha ao calcular panorama."));
            return;
        }
        
        aplicarValores(data);
        const btnSalvar = document.getElementById("btn-salvar");
        if(btnSalvar) {
            btnSalvar.setAttribute("data-periodo", periodo);
            btnSalvar.style.display = "inline-block";
        }
    } catch (e) { 
        console.error("Erro na requisição", e); 
        alert("Erro de conexão ao buscar panorama.");
    }
}

function aplicarValores(data) {
    const format = (val) => {
        if (val === undefined || val === null) return 'R$ 0,0 mi';
        let num = Math.abs(val) / 1000000;
        let prefix = val < 0 ? '-R$ ' : 'R$ ';
        return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
    };

    const map = [
        { keys: ['caixa e equivalente', 'caixa'], val: data.caixa_bp },
        { keys: ['ativo total'], val: data.ativo_total },
        { keys: ['passivo total'], val: data.passivo_total },
        { keys: ['patrimônio líquido', 'patrimonio liquido'], val: data.patrimonio_liquido },
        { keys: ['receitas realizadas', 'receita realizada'], val: data.receita_realizada },
        { keys: ['despesas empenhadas', 'despesa empenhada'], val: data.despesa_empenhada },
        { keys: ['superávit orçamentário', 'superavit orcamentario', 'déficit orçamentário', 'deficit orcamentario'], val: data.superavit_orcamentario },
        { keys: ['superávit patrimonial', 'superavit patrimonial'], val: data.superavit_patrimonial },
        { keys: ['superávit financeiro', 'superavit financeiro'], val: data.superavit_financeiro }
    ];

    document.querySelectorAll('*').forEach(el => {
        if (el.children.length > 0) return;
        let txt = el.innerText ? el.innerText.toLowerCase().trim() : '';

        for (let item of map) {
            if (item.keys.some(k => txt.includes(k))) {
                let card = el.parentElement;
                if (!card) continue;
                let atualizado = false;
                Array.from(card.querySelectorAll('*')).forEach(child => {
                    if (atualizado || child === el || child.children.length > 0) return;
                    let cTxt = child.innerText.trim();
                    if (cTxt.includes('R$') || cTxt.includes('0,0') || cTxt.includes('0,00')) {
                        child.innerText = format(item.val);
                        atualizado = true;
                    }
                });
                if (!atualizado && el.nextElementSibling) {
                    let next = el.nextElementSibling;
                    if (next.innerText.includes('R$') || next.innerText.includes('0,0')) {
                        next.innerText = format(item.val);
                    }
                }
            }
        }
    });
}

async function salvarPanorama() {
    const btn = document.getElementById("btn-salvar");
    const periodo = btn.getAttribute("data-periodo");
    if (!periodo) { alert("Clique em 'Verificar' antes de salvar."); return; }
    
    const txtOriginal = btn.innerText;
    btn.innerText = "Salvando..."; btn.disabled = true;
    try {
        const res = await fetch("/salvar_panorama/" + periodo, { method: "POST" });
        if(res.ok) {
            alert("Resultados salvos com sucesso!");
            carregarHistorico();
        } else {
            alert("Erro ao salvar no servidor.");
        }
    } catch (e) { 
        alert("Erro de conexão ao salvar."); 
    } finally { 
        btn.innerText = txtOriginal; btn.disabled = false; 
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
        // Busca os dados salvos no histórico
        const res = await fetch(`/historico_panorama/${check.value}`);
        const data = await res.json();
        if (data.erro) { alert("Erro ao carregar histórico."); return; }
        
        // A API retorna o JSON salvo, então aplicamos na tela
        aplicarValores(data.dados || data); 
        
        // Rola a tela para o topo para ver os valores
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

// ===== EVENT LISTENERS (ÚNICA FONTE DA VERDADE) =====
document.addEventListener("DOMContentLoaded", function() {
    const bind = (id, fn) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('click', function(e){ e.preventDefault(); fn(); });
    };

    bind('btn-verificar', carregarPanorama);
    bind('btn-salvar', salvarPanorama);
    bind('btn-exibir', exibirSelecionado);
    bind('btn-excluir', excluirSelecionado);
    bind('btn-pdf', gerarPDFPanorama);

    carregarHistorico();
});
"""

# Substitui o último bloco de script que tem "carregarPanorama" pelo nosso novo
scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE))
for m in reversed(scripts):
    if 'carregarPanorama' in m.group(1):
        html = html[:m.start(1)] + novo_js + html[m.end(1):]
        break

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Frontend reescrito e limpo (sem duplicidade de eventos).")
print("[OK] 'Exibir Selecionado' agora puxa os dados do histórico sem abrir nova aba.")
print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador: http://127.0.0.1:9994/panorama")
print("2. Aperte Ctrl + Shift + R (MUITO IMPORTANTE).")
print("3. Teste todos os botoes (Verificar, Salvar, Exibir, Excluir, PDF).")
