import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. BACKEND: CRIAR ROTA DE SALVAR CONCLUSÃO
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_edit_conc_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

if "/salvar_conclusao_centro_custos/" not in c_back:
    nova_rota = '''
@app.post("/salvar_conclusao_centro_custos/{historico_id}")
async def salvar_conclusao_centro_custos(historico_id: int, request: Request):
    import sqlite3, json, os
    try:
        data = await request.json()
        texto = data.get("texto", "")
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT dados_json FROM historico_centro_custos WHERE id = ?", (historico_id,))
        row = cur.fetchone()
        
        if row:
            dados = json.loads(row[0])
            dados["conclusao_personalizada"] = texto
            cur.execute("UPDATE historico_centro_custos SET dados_json = ? WHERE id = ?", (json.dumps(dados), historico_id))
            conn.commit()
            conn.close()
            return {"erro": False, "mensagem": "Conclusão salva com sucesso!"}
        
        conn.close()
        return {"erro": True, "mensagem": "Histórico não encontrado."}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''
    c_back += nova_rota
    # Garante a importação do Request
    if "from fastapi import Request" not in c_back and "from fastapi import" in c_back:
        c_back = c_back.replace("from fastapi import", "from fastapi import Request,", 1)
    elif "from fastapi import Request" not in c_back:
        c_back = "from fastapi import Request\n" + c_back

    open(back_path, 'w', encoding='utf-8').write(c_back)
    print("[OK] Rota de Salvar Conclusão criada no Backend!")
else:
    print("[AVISO] Rota já existia no Backend.")

# ==========================================
# 2. FRONTEND: BOTÃO E MODAL NA TELA PRINCIPAL (analise_centro_custos.html)
# ==========================================
front_main = r"pc_frontend\analise_centro_custos.html"
shutil.copy2(front_main, f"{front_main}.bak_edit_conc_{ts}")
c = open(front_main, encoding='utf-8').read()

# Injeta o botão ao lado do Gerar PDF
if 'id="btn-editar-conclusao"' not in c:
    # Procura o botão de PDF para colocar do lado
    match_btn = re.search(r'(<button[^>]*>Gerar PDF</button>)', c, re.IGNORECASE)
    if match_btn:
        btn_edit = '<button id="btn-editar-conclusao" class="btn" style="background:#f59e0b; color:white; margin-left:10px;" onclick="abrirModalConclusao()">✏️ Editar Conclusão</button>'
        c = c.replace(match_btn.group(1), match_btn.group(1) + "\n" + btn_edit)

# Injeta o Modal e a Lógica JS no final da página
js_modal = """
    <script>
        function abrirModalConclusao() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Atenção: Selecione um item do Histórico Salvo primeiro."); return; }
            
            const id = check.value;
            
            fetch(`/historico_centro_custos/${id}`)
                .then(res => res.json())
                .then(data => {
                    const textoAtual = (data.dados && data.dados.conclusao_personalizada) ? data.dados.conclusao_personalizada : "";
                    
                    const divModal = document.createElement('div');
                    divModal.id = 'modal-conclusao';
                    divModal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
                    divModal.innerHTML = `
                        <div style="background:#fff;padding:20px;border-radius:8px;width:600px;max-width:90%;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                            <h3 style="margin-top:0;color:#1a202c;">Editar Conclusão do Relatório</h3>
                            <p style="font-size:14px;color:#718096;margin-bottom:10px;">Este texto substituirá a conclusão automática no PDF.</p>
                            <textarea id="txt-conclusao" style="width:100%;height:150px;padding:10px;border:1px solid #cbd5e0;border-radius:4px;font-family:inherit;font-size:14px;">${textoAtual}</textarea>
                            <div style="margin-top:15px;text-align:right;">
                                <button onclick="document.getElementById('modal-conclusao').remove()" style="padding:8px 15px;margin-right:10px;border:none;border-radius:4px;background:#e2e8f0;color:#4a5568;font-weight:bold;cursor:pointer;">Cancelar</button>
                                <button onclick="salvarConclusao(${id})" style="padding:8px 15px;border:none;border-radius:4px;background:#38a169;color:white;font-weight:bold;cursor:pointer;">Salvar Conclusão</button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(divModal);
                })
                .catch(() => alert("Erro ao carregar o histórico."));
        }

        function salvarConclusao(id) {
            const texto = document.getElementById('txt-conclusao').value;
            fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({texto: texto})
            })
            .then(res => res.json())
            .then(data => {
                if (data.erro) { alert("Erro: " + data.mensagem); }
                else { 
                    alert("Conclusão salva com sucesso! O PDF usará este texto.");
                    document.getElementById('modal-conclusao').remove();
                }
            })
            .catch(() => alert("Erro de conexão ao salvar."));
        }
    </script>
"""

if '</body>' in c:
    c = c.replace('</body>', js_modal + '\n</body>', 1)
else:
    c += js_modal

open(front_main, 'w', encoding='utf-8').write(c)
print("[OK] Botão e modal de edição adicionados na tela principal!")

# ==========================================
# 3. FRONTEND: INJETAR A CONCLUSÃO NO PDF (relatorio_centro_custos.html)
# ==========================================
arquivo_rel = r"pc_frontend\relatorio_centro_custos.html"
shutil.copy2(arquivo_rel, f"{arquivo_rel}.bak_edit_conc_{ts}")
c_rel = open(arquivo_rel, encoding='utf-8').read()

# Remove o espião antigo se existir
c_rel = re.sub(r'<script id="interceptar_historico">.*?</script>', '', c_rel, flags=re.DOTALL)

novo_espiao = """
    <script id="interceptar_historico">
        (function() {
            const urlParams = new URLSearchParams(window.location.search);
            const historicoId = urlParams.get('historico_id');
            
            if (historicoId) {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('/api/relatorio_v2/') || url.includes('/api/centro_custos/')) {
                        return originalFetch(`/historico_centro_custos/${historicoId}`, options)
                            .then(res => res.json())
                            .then(data => {
                                const dados = data.dados ? data.dados : data;
                                const centros = dados.centros || [];
                                const centrosAnt = dados.centros_anterior || [];

                                const totalAtual = centros.reduce((acc, c) => acc + c.valor, 0);
                                const totalAnterior = centrosAnt.reduce((acc, c) => acc + c.valor, 0);
                                const variacao_pct = totalAnterior > 0 ? ((totalAtual - totalAnterior) / totalAnterior) * 100 : 0;
                                
                                let maiorCentro = { nome: "Nenhum", valor: 0 };
                                if (centros.length > 0) {
                                    maiorCentro = centros.reduce((max, c) => c.valor > max.valor ? c : max, centros[0]);
                                }

                                const respostaFinal = {
                                    atual: { total: totalAtual, media_mensal: totalAtual / 9, maior_centro: maiorCentro },
                                    anterior: { total: totalAnterior, media_mensal: totalAnterior / 9 },
                                    variacao_pct: variacao_pct,
                                    centros: centros,
                                    centros_anterior: centrosAnt
                                };

                                return new Response(JSON.stringify(respostaFinal), { 
                                    headers: { 'Content-Type': 'application/json' } 
                                });
                            });
                    }
                    return originalFetch(url, options);
                };

                // Injeta o texto personalizado na tela após o carregamento
                window.addEventListener('load', () => {
                    fetch(`/historico_centro_custos/${historicoId}`)
                        .then(r => r.json())
                        .then(data => {
                            const dados = data.dados ? data.dados : data;
                            if (dados.conclusao_personalizada) {
                                // Encontra o título da conclusão e substitui o texto abaixo dele
                                const allHeaders = document.querySelectorAll('h1, h2, h3');
                                for (let h of allHeaders) {
                                    const txt = h.innerText.toUpperCase();
                                    if (txt.includes('CONCLUSÃO') || txt.includes('RECOMENDAÇÕES')) {
                                        let parent = h.parentElement;
                                        // Substitui o conteúdo do bloco inteiro, mantendo o título
                                        parent.innerHTML = `<h2 style="color:#0a1c3a; font-size:16px; margin-bottom:10px;">${h.innerText}</h2><div style="white-space: pre-wrap; font-size:14px; line-height:1.6; text-align:justify;">${dados.conclusao_personalizada}</div>`;
                                        break;
                                    }
                                }
                            }
                        });
                });
            }
        })();
    </script>
"""

if '</body>' in c_rel:
    c_rel = c_rel.replace('</body>', novo_espiao + '\n</body>', 1)
else:
    c_rel += novo_espiao

open(arquivo_rel, 'w', encoding='utf-8').write(c_rel)
print("[OK] Relatório ajustado para injetar a conclusão personalizada no PDF!")

# Validar sintaxe do Python
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Erro de sintaxe no main.py: {e}")
