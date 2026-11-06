import re, shutil, datetime, sqlite3, os

# =========================================================
# 1. LIMPAR O BANCO DE DADOS (Apagar historico bugado)
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
# 2. BACKEND: salvar_panorama calcula sozinho (sem deadlock)
# =========================================================
arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

padrao_rota = re.compile(r'@app\.post\("/salvar_panorama/\{periodo\}"\).*?(?=\n@app\.|\Z)', re.DOTALL)

nova_rota = '''@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str):
    import sqlite3, json, os, datetime
    try:
        # O backend calcula os valores ele mesmo (chamando a funcao Python diretamente)
        dados = await api_panorama(periodo)
        
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
print("[OK] Backend ajustado: salva usando o calculo proprio do Python.")

# =========================================================
# 3. FRONTEND: Botao salvar envia so o periodo, exibir formata certinho
# =========================================================
arq_html = r"pc_frontend\panorama.html"
shutil.copy2(arq_html, f"pc_frontend\\panorama_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

novo_js = """
        // ===== FUNÇÕES CORE =====
        const fmt = (val) => {
            if (val === undefined || val === null) return 'R$ 0,0 mi';
            let num = parseFloat(val);
            if (isNaN(num)) return 'R$ 0,0 mi';
            let absNum = Math.abs(num) / 1000000;
            let sinal = num < 0 ? '-R$ ' : 'R$ ';
            return sinal + absNum.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
        };

        function aplicarValores(data) {
            let d = data;
            if (d && d.dados) d = d.dados;
            if (typeof d === 'string') {
                try { d = JSON.parse(d); } catch(e) {}
            }
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
                // Envia apenas a ordem de salvar, o backend calcula
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
                if (!res.ok) throw new Error("Erro HTTP " + res.status);
                
                const data = await res.json();
                if (data.erro) { alert("Erro no servidor: " + data.erro); return; }
                
                aplicarValores(data); 
                window.scrollTo(0, 0);
            } catch(e) {
                console.error("Falha no exibir:", e);
                alert("Erro ao carregar o histórico. Verifique o Console (F12).");
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

        document.addEventListener("DOMContentLoaded", () => {
            document.getElementById('btn-verificar').addEventListener('click', carregarPanorama);
            document.getElementById('btn-salvar').addEventListener('click', salvarPanorama);
            document.getElementById('btn-exibir').addEventListener('click', exibirSelecionado);
            document.getElementById('btn-excluir').addEventListener('click', excluirSelecionado);
            document.getElementById('btn-pdf').addEventListener('click', gerarPDFPanorama);

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
print("[OK] Frontend atualizado (Salvar envia so o pedido, Exibir formata).")

print("\n==============================================")
print("=== AÇÃO OBRIGATÓRIA: REINICIAR O SERVIDOR ===")
print("==============================================")
print("1. No terminal do uvicorn, aperte Ctrl+C.")
print("2. Suba de novo: cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. Va no navegador: http://127.0.0.1:9994/panorama")
print("4. Aperte Ctrl+Shift+R.")
print("5. Clique em Verificar, depois Salvar. E depois Exibir no item novo.")
