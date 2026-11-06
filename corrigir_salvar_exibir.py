import re, shutil, datetime

# =========================================================
# 1. AJUSTAR O FRONTEND (panorama.html)
# =========================================================
arq_html = r"pc_frontend\panorama.html"
shutil.copy2(arq_html, f"pc_frontend\\panorama_backup_fix_salvar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Altera a função salvarPanorama para pegar os dados da tela e enviar no corpo da requisição
nova_funcao_salvar = """async function salvarPanorama() {
            const btn = document.getElementById("btn-salvar");
            const periodo = btn.getAttribute("data-periodo");
            if (!periodo) { alert("Verifique o panorama antes de salvar."); return; }
            
            // Coleta os valores da tela no momento do clique
            const dadosTela = {
                ativo_total:      document.getElementById('val-ativo').innerText,
                passivo_total:    document.getElementById('val-passivo').innerText,
                patrimonio_liquido: document.getElementById('val-pl').innerText,
                caixa_bp:         document.getElementById('val-caixa').innerText,
                receita_realizada: document.getElementById('val-receitas').innerText,
                despesa_empenhada: document.getElementById('val-despesas').innerText,
                superavit_orcamentario: document.getElementById('val-superavit-orc').innerText,
                superavit_patrimonial:  document.getElementById('val-superavit-pat').innerText,
                superavit_financeiro:   document.getElementById('val-superavit-fin').innerText
            };
            
            btn.innerText = "Salvando..."; 
            btn.disabled = true;
            
            try {
                const res = await fetch("/salvar_panorama/" + periodo, { 
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(dadosTela)
                });
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
        }"""

padrao_salvar = re.compile(r'async function salvarPanorama\(\)\s*\{.*?\n        \}', re.DOTALL)
html = padrao_salvar.sub(nova_funcao_salvar, html)

with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Frontend alterado para enviar os dados da tela no POST.")

# =========================================================
# 2. AJUSTAR O BACKEND (main.py)
# =========================================================
arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_fix_salvar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

padrao_rota = re.compile(r'@app\.post\("/salvar_panorama/\{periodo\}"\).*?(?=\n@app\.|\Z)', re.DOTALL)

nova_rota = '''@app.post("/salvar_panorama/{periodo}")
async def salvar_panorama(periodo: str, request: Request):
    import sqlite3, json, os, datetime
    from fastapi import Request
    try:
        # Pega o JSON enviado pelo frontend
        dados_tela = await request.json()
        
        # Converte os valores formatados ("R$ 616,6 mi") para float caso seja necessário, 
        # mas vamos salvar do jeito que veio para a tela exibir idêntico.
        # Para o PDF funcionar, precisamos dos números absolutos.
        # Vamos limpar a string e converter de volta para float.
        def parse_valor(s):
            if isinstance(s, (int, float)): return float(s)
            s = str(s).replace("R$", "").replace("mi", "").replace(".", "").replace(",", ".").strip()
            try: return float(s) * 1000000
            except: return 0.0

        dados_limpos = {
            "ativo_total": parse_valor(dados_tela.get("ativo_total")),
            "passivo_total": parse_valor(dados_tela.get("passivo_total")),
            "patrimonio_liquido": parse_valor(dados_tela.get("patrimonio_liquido")),
            "caixa_bp": parse_valor(dados_tela.get("caixa_bp")),
            "receita_realizada": parse_valor(dados_tela.get("receita_realizada")),
            "despesa_empenhada": parse_valor(dados_tela.get("despesa_empenhada")),
            "superavit_orcamentario": parse_valor(dados_tela.get("superavit_orcamentario")),
            "superavit_patrimonial": parse_valor(dados_tela.get("superavit_patrimonial")),
            "superavit_financeiro": parse_valor(dados_tela.get("superavit_financeiro")),
        }

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS historico_panorama (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO historico_panorama (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                       (periodo, data_agora, json.dumps(dados_limpos, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Salvo com sucesso"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}
'''

main_code = padrao_rota.sub(nova_rota, main_code)

# Adiciona o import do Request no topo, se não existir
if "from fastapi import Request" not in main_code:
    main_code = main_code.replace("from fastapi import FastAPI", "from fastapi import FastAPI, Request")

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)
print("[OK] Backend alterado para ler o JSON do frontend e salvar no banco.")

print("\n==============================================")
print("=== AÇÃO OBRIGATÓRIA: REINICIAR O SERVIDOR ===")
print("==============================================")
print("1. No terminal do uvicorn, aperte Ctrl+C.")
print("2. Suba de novo: cd pc_backend; ..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 9994")
print("3. Va no navegador: http://127.0.0.1:9994/panorama")
print("4. Aperte Ctrl+Shift+R.")
print("5. Clique em Verificar, depois Salvar. E depois Exibir no item novo do historico.")
