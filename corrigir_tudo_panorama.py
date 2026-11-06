import re, shutil, datetime, os

# 1. LER O MAIN.PY E CONSERTAR A ROTA SALVAR_PANORAMA
arq_main = r"pc_backend\main.py"
backup_main = f"pc_backend\\main_backup_salvar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(arq_main, backup_main)
print(f"[OK] Backup main.py: {backup_main}")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Encontra a rota salvar_panorama
match = re.search(r'@app\.post\("/salvar_panorama/\{periodo\}"\).*?(?=\n@app\.|\Z)', main_code, re.DOTALL)
if match:
    rota_antiga = match.group(0)
    
    # Nova rota: chama a API correta via funcao local ou urllib, e salva no banco
    nova_rota = '''@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str):
    import sqlite3, json, os, datetime
    import urllib.request
    try:
        # Chama a propria API do panorama que calcula os valores CERTOS
        url = f"http://127.0.0.1:9994/api/panorama/{periodo}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            dados = json.loads(response.read().decode())
            
        if dados.get("erro"):
            return {"erro": True, "mensagem": dados.get("mensagem")}
            
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_panorama (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_panorama (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    main_code = main_code.replace(rota_antiga, nova_rota)
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("[OK] Rota salvar_panorama no main.py corrigida para salvar os dados reais.")
else:
    print("[AVISO] Nao achei a rota salvar_panorama no main.py. Ela pode estar em outro arquivo.")

# 2. LIMPAR O BANCO E REESCREVER O FRONTEND
db_path = os.path.join("pc_storage", "banco_dados.db")
try:
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.cursor().execute("DELETE FROM historico_panorama")
    conn.commit()
    conn.close()
    print("[OK] Historico errado apagado do banco.")
except Exception as e:
    print(f"[AVISO] Nao foi possivel limpar o banco: {e}")

arq_html = r"pc_frontend\panorama.html"
backup_html = f"pc_frontend\\panorama_backup_total_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
shutil.copy2(arq_html, backup_html)
print(f"[OK] Backup panorama.html: {backup_html}")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Vamos recriar a estrutura dos cards do zero para garantir IDs corretos
# Substitui todo o bloco de divs (cards) por um novo
cards_html = """
<div class="cards-grid" style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px;">
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Caixa e Equivalente de Caixa (BP)</div>
        <div id="val-caixa" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Ativo Total</div>
        <div id="val-ativo" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Passivo Total</div>
        <div id="val-passivo" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Patrimônio Líquido</div>
        <div id="val-pl" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Receitas Realizadas (BO)</div>
        <div id="val-receitas" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Despesas Empenhadas (BO)</div>
        <div id="val-despesas" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Superávit Orçamentário</div>
        <div id="val-superavit-orc" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Superávit Patrimonial (DVP)</div>
        <div id="val-superavit-pat" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
    <div class="card" style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3;">
        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Superávit Financeiro (BP)</div>
        <div id="val-superavit-fin" style="font-size: 24px; font-weight: bold; color: #333;">R$ 0,0 mi</div>
    </div>
</div>
"""

# Tenta achar o miolo onde estavam os cards antigos e substitui
# Vamos procurar entre "<div class=\"cards-grid" e o final desse bloco.
# Se nao achar, apenas ignoramos (pode ja ter sido substituido antes).
html = re.sub(r'<div class="cards-grid".*?</div>\s*</div>\s*</div>', cards_html, html, flags=re.DOTALL | re.IGNORECASE)

# 3. REESCREVER O JAVASCRIPT
novo_js = """
// ===== JAVASCRIPT DEFINITIVO 6.0 - PANORAMA =====

function aplicarValores(data) {
    let d = data;
    if (d && d.dados) d = d.dados;
    if (typeof d === 'string') d = JSON.parse(d);
    if (d && d.dados) d = d.dados; 

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
    setVal('val-pl', d.patrimonio_liquido);
    setVal('val-receitas', d.receita_realizada);
    setVal('val-despesas', d.despesa_empenhada);
    setVal('val-superavit-orc', d.superavit_orcamentario);
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

with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html)

print("\n[OK] TUDO PRONTO!")
print("=== PROXIMO PASSO ===")
print("1. REINICIE O SERVIDOR (Ctrl+C e suba de novo) para o main.py valer.")
print("2. Va no navegador: http://127.0.0.1:9994/panorama")
print("3. Aperte Ctrl + Shift + R.")
print("4. Clique em Verificar, depois Salvar. E teste o Exibir no historico novo.")
