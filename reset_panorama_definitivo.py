import shutil, datetime, sqlite3, os, re

# =========================================================
# 1. CONSERTAR O BACKEND (main.py)
# =========================================================
arq_main = r"pc_backend\main.py"
backup_main = f"pc_backend\\main_backup_salvar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(arq_main, backup_main)
print(f"[OK] Backup main.py: {backup_main}")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Substitui a rota de salvar por uma que chama o cálculo local e salva o JSON certinho
padrao_rota = re.compile(r'@app\.post\("/salvar_panorama/\{periodo\}"\).*?(?=\n@app\.|\Z)', re.DOTALL)
if padrao_rota.search(main_code):
    nova_rota = '''@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str):
    import sqlite3, json, os, datetime
    import urllib.request
    try:
        # Puxa os dados da API local para garantir que são os dados certos
        url = f"http://127.0.0.1:9994/api/panorama/{periodo}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            dados = json.loads(response.read().decode())
            
        if dados.get("erro"):
            return {"erro": True, "mensagem": dados.get("mensagem", "Erro no calculo")}
            
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
    main_code = padrao_rota.sub(nova_rota, main_code)
    with open(arq_main, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("[OK] Rota /salvar_panorama/ corrigida no main.py.")
else:
    print("[AVISO] Rota salvar_panorama nao encontrada no main.py.")

# =========================================================
# 2. LIMPAR O BANCO DE DADOS
# =========================================================
try:
    db_path = os.path.join("pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    conn.cursor().execute("DELETE FROM historico_panorama")
    conn.commit()
    conn.close()
    print("[OK] Histórico antigo e bugado apagado do banco.")
except Exception as e:
    print(f"[AVISO] Nao foi possivel limpar o banco: {e}")

# =========================================================
# 3. RECONSTRUIR O PANORAMA.HTML DO ZERO
# =========================================================
arq_html = r"pc_frontend\panorama.html"
backup_html = f"pc_frontend\\panorama_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
shutil.copy2(arq_html, backup_html)
print(f"[OK] Backup panorama.html: {backup_html}")

html_limpo = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panorama de Resultados</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: #f4f6f9; padding: 20px; color: #333; }
        
        .top-bar { display: flex; gap: 10px; margin-bottom: 20px; align-items: center; flex-wrap: wrap; }
        .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .btn-voltar { background: #ff7f00; color: white; text-decoration: none; }
        .btn-verde { background: #28a745; color: white; }
        .btn-vermelho { background: #dc3545; color: white; }
        .btn-azul { background: #0056b3; color: white; }
        .btn:hover { opacity: 0.9; }
        
        .filtros { display: flex; gap: 15px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; align-items: center; flex-wrap: wrap; }
        .filtros label { font-size: 12px; font-weight: bold; color: #555; }
        .filtros select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        
        .layout { display: flex; gap: 20px; }
        
        .sidebar { width: 250px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: fit-content; }
        .sidebar h3 { margin-top: 0; font-size: 16px; color: #003366; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .sidebar ul { list-style: none; padding: 0; }
        .sidebar li { margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px; }
        .sidebar .check-historico { width: 16px; height: 16px; cursor: pointer; }
        .sidebar .periodo { font-weight: bold; color: #0056b3; }
        .sidebar .data { font-size: 12px; color: #888; }
        
        .main-content { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .main-content h2 { margin-top: 0; color: #003366; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0056b3; }
        .card .label { font-size: 12px; color: #666; margin-bottom: 5px; }
        .card .valor { font-size: 24px; font-weight: bold; color: #333; }
        
        .footer { margin-top: 40px; font-size: 11px; color: #999; border-top: 1px solid #ddd; padding-top: 10px; display: flex; justify-content: space-between; }
    </style>
</head>
<body>

    <div class="top-bar">
        <a href="/" class="btn btn-voltar">← Voltar</a>
        <button id="btn-exibir" class="btn btn-verde">Exibir Selecionado</button>
        <button id="btn-excluir" class="btn btn-vermelho">Excluir Selecionado</button>
        <button id="btn-pdf" class="btn btn-azul">Gerar PDF</button>
        <button id="btn-salvar" class="btn btn-verde" style="display:none;">Confirmar e Salvar</button>
    </div>

    <div class="filtros">
        <div>
            <label>Ano:</label>
            <select id="ano">
                <option value="2026">2026</option>
            </select>
        </div>
        <div>
            <label>Tipo:</label>
            <select id="tipo_periodo">
                <option value="TRIMESTRE">Trimestral</option>
            </select>
        </div>
        <div>
            <label>Trimestre:</label>
            <select id="trimestre">
                <option value="1">1º Trimestre</option>
                <option value="2">2º Trimestre</option>
                <option value="3">3º Trimestre</option>
                <option value="4">4º Trimestre</option>
            </select>
        </div>
        <button id="btn-verificar" class="btn btn-azul">Verificar</button>
    </div>

    <div class="layout">
        <div class="sidebar">
            <h3>Histórico Salvo</h3>
            <ul id="lista-historico">
                <li>Carregando...</li>
            </ul>
        </div>

        <div class="main-content">
            <p style="font-size: 12px; color: #888; font-weight: bold;">PANORAMA</p>
            <h2 id="periodo-titulo">Resultados Gerais</h2>
            
            <div class="cards-grid">
                <div class="card">
                    <div class="label">Caixa e Equivalente de Caixa (BP)</div>
                    <div class="valor" id="val-caixa">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Ativo Total</div>
                    <div class="valor" id="val-ativo">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Passivo Total</div>
                    <div class="valor" id="val-passivo">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Patrimônio Líquido</div>
                    <div class="valor" id="val-pl">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Receitas Realizadas (BO)</div>
                    <div class="valor" id="val-receitas">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Despesas Empenhadas (BO)</div>
                    <div class="valor" id="val-despesas">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Superávit Orçamentário</div>
                    <div class="valor" id="val-superavit-orc">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Superávit Patrimonial (DVP)</div>
                    <div class="valor" id="val-superavit-pat">R$ 0,0 mi</div>
                </div>
                <div class="card">
                    <div class="label">Superávit Financeiro (BP)</div>
                    <div class="valor" id="val-superavit-fin">R$ 0,0 mi</div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div>Cofen • Análise das Demonstrações Contábeis</div>
        <div>SGPC - Sistema de Gestão de Prestação de Contas</div>
    </div>

    <script>
        // ===== FUNÇÕES CORE =====
        const fmt = (val) => {
            if (val === undefined || val === null || isNaN(val)) return 'R$ 0,0 mi';
            let num = Math.abs(val) / 1000000;
            let prefix = val < 0 ? '-R$ ' : 'R$ ';
            return prefix + num.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
        };

        function aplicarValores(data) {
            let d = data;
            if (d && d.dados) d = d.dados;
            if (typeof d === 'string') d = JSON.parse(d);
            if (d && d.dados) d = d.dados;

            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.innerText = fmt(val);
            };

            setVal('val-caixa', d.caixa_bp);
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
            const valor = document.getElementById('trimestre').value;
            const periodo = `${ano}-${tipo}-${valor}`;
            
            document.getElementById('periodo-titulo').innerText = `Resultados Gerais — ${valor}º Trimestre de ${ano}`;
            
            try {
                const response = await fetch(`/api/panorama/${periodo}`);
                const data = await response.json();
                
                if (data.erro) { alert("Erro: " + (data.mensagem || "Faltam peças")); return; }
                
                aplicarValores(data);
                
                const btnSalvar = document.getElementById("btn-salvar");
                btnSalvar.setAttribute("data-periodo", periodo);
                btnSalvar.style.display = "inline-block";
                btnSalvar.innerText = "Confirmar e Salvar";
                btnSalvar.disabled = false;
            } catch (e) { 
                console.error(e); 
                alert("Erro de conexão ao buscar panorama.");
            }
        }

        async function salvarPanorama() {
            const btn = document.getElementById("btn-salvar");
            const periodo = btn.getAttribute("data-periodo");
            if (!periodo) { alert("Verifique o panorama antes de salvar."); return; }
            
            btn.innerText = "Salvando..."; 
            btn.disabled = true;
            
            try {
                const res = await fetch("/salvar_panorama/" + periodo, { method: "POST" });
                if(res.ok) {
                    alert("Resultados salvos com sucesso!");
                    carregarHistorico();
                } else {
                    alert("Erro no servidor ao salvar.");
                }
            } catch (e) { 
                alert("Erro de conexão ao salvar."); 
            } finally { 
                btn.innerText = "Confirmar e Salvar"; 
                btn.disabled = false; 
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
                            html += `<li>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <input type="checkbox" class="check-historico" value="${item.id}">
                                    <div>
                                        <div class="periodo">${item.periodo}</div>
                                        <div class="data">Gerado em: ${item.data_geracao}</div>
                                    </div>
                                </div>
                            </li>`;
                        });
                    }
                    document.getElementById('lista-historico').innerHTML = html;
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

        // ===== LIGANDO OS BOTOES (ÚNICA FONTE DA VERDADE) =====
        document.addEventListener("DOMContentLoaded", () => {
            document.getElementById('btn-verificar').addEventListener('click', carregarPanorama);
            document.getElementById('btn-salvar').addEventListener('click', salvarPanorama);
            document.getElementById('btn-exibir').addEventListener('click', exibirSelecionado);
            document.getElementById('btn-excluir').addEventListener('click', excluirSelecionado);
            document.getElementById('btn-pdf').addEventListener('click', gerarPDFPanorama);

            carregarHistorico();
        });
    </script>
</body>
</html>
"""

with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html_limpo)

print("[OK] panorama.html refeito do zero (HTML limpo e JS à prova de falhas).")
print("\n==============================================")
print("=== AÇÃO NECESSÁRIA: REINICIAR O SERVIDOR ===")
print("==============================================")
print("1. No terminal do uvicorn, aperte Ctrl+C.")
print("2. Suba novamente: cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. Va no navegador: http://127.0.0.1:9994/panorama")
print("4. Aperte Ctrl+Shift+R e teste tudo.")
