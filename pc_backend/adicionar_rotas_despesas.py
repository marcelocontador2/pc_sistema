c = open('main.py', encoding='utf-8-sig').read()

if 'def api_comparativo_despesas_v2' not in c:
    novas_rotas = r'''
# ========== ROTAS DO COMPARATIVO DE DESPESAS ==========
@app.get("/api/comparativo_despesas_v2/{periodo_atual}")
def api_comparativo_despesas_v2(periodo_atual: str):
    import os, re
    upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"
    partes = periodo_atual.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None
    
    def parse_valor(s):
        s = s.strip().strip('"').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try:
            return float(s)
        except:
            return 0.0
    
    def parse_pct(s):
        s = s.strip().strip('"').replace("%", "").replace(",", ".").strip()
        try:
            return float(s)
        except:
            return 0.0
    
    def ler_csv(periodo):
        if not periodo: return None
        periodo_formatado = periodo.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_DESPESAS_{periodo_formatado}.csv")
        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_DESPESAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break
        if not os.path.exists(arquivo):
            return None
        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f: linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f: linhas = f.readlines()
            
            dados = {"orcado_total": 0.0, "realizado_total": 0.0, "empenhado_total": 0.0, "percentual_total": 0.0, "grupos": []}
            grupos_nomes = ["DESPESAS CORRENTES", "DESPESAS DE CAPITAL", "PESSOAL E ENCARGOS SOCIAIS", "OUTRAS DESPESAS CORRENTES", "INVESTIMENTOS"]
            
            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue
                nome = partes_linha[0].strip().strip('"')
                if not nome: continue
                
                if "TOTAL" in nome.upper() or "DESPESA REALIZADA" in nome.upper():
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["realizado_total"] = parse_valor(partes_linha[2])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])
                elif nome in grupos_nomes:
                    dados["grupos"].append({
                        "nome": nome,
                        "orcado": parse_valor(partes_linha[1]),
                        "realizado": parse_valor(partes_linha[2]),
                        "empenhado": parse_valor(partes_linha[2]),
                        "percentual": parse_pct(partes_linha[3])
                    })
            return dados
        except:
            return None
    
    atual = ler_csv(periodo_atual)
    anterior = ler_csv(periodo_anterior)
    if not atual:
        return {"erro": True, "mensagem": "Dados não encontrados para o período atual."}
    return {"erro": False, "periodo_atual": periodo_atual, "periodo_anterior": periodo_anterior, "atual": atual, "anterior": anterior or {"orcado_total": 0, "realizado_total": 0, "empenhado_total": 0, "percentual_total": 0, "grupos": []}}

@app.get("/historico_comparativo_despesas")
def get_historico_comparativo_despesas():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_despesas (id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    conn.commit()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_comparativo_despesas ORDER BY id DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

@app.get("/historico_comparativo_despesas/{id}")
def get_historico_comparativo_despesas_id(id: int):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("SELECT periodo, dados_json FROM historico_comparativo_despesas WHERE id = ?", (id,))
    row = cur.fetchone(); conn.close()
    if row: return {"ok": True, "periodo": row[0], "dados": json.loads(row[1])}
    return {"ok": False}

@app.post("/salvar_comparativo_despesas")
async def salvar_comparativo_despesas(request: Request):
    import sqlite3, os, json
    from datetime import datetime
    dados = await request.json()
    periodo = dados.get("periodo", "2026-TRIMESTRE-3")
    dados_json = json.dumps(dados.get("dados", {}))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    cur.execute("INSERT INTO historico_comparativo_despesas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo, data_geracao, dados_json))
    conn.commit(); conn.close()
    return {"ok": True}

@app.post("/excluir_multiplos_comparativo_despesas")
async def excluir_multiplos_comparativo_despesas(request: Request):
    import sqlite3, os
    dados = await request.json()
    ids = dados.get("ids", [])
    if not ids: return {"ok": False}
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path); cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ids))
    cur.execute(f"DELETE FROM historico_comparativo_despesas WHERE id IN ({placeholders})", ids)
    conn.commit(); excluidos = cur.rowcount; conn.close()
    return {"ok": True, "excluidos": excluidos}

@app.get("/analise_comparativo_despesas", response_class=HTMLResponse)
def serve_analise_comparativo_despesas():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "analise_comparativo_despesas.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
    return HTMLResponse(content="<h1>Tela não encontrada</h1>", status_code=404)

@app.get("/gerar_pdf_comparativo_despesas")
def gerar_pdf_comparativo_despesas(periodo_atual: str = "2026-TRIMESTRE-3"):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import time, os
    url = f"http://127.0.0.1:9994/relatorio_comparativo_despesas?periodo_atual={periodo_atual}&_t={int(time.time())}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(bypass_csp=True)
        page = context.new_page()
        page.set_extra_http_headers({"Cache-Control": "no-cache, no-store, must-revalidate"})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"})
        browser.close()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=relatorio_despesas_{periodo_atual}.pdf"})
'''
    if 'if __name__ == "__main__":' in c:
        c = c.replace('if __name__ == "__main__":', novas_rotas + '\nif __name__ == "__main__":')
    else:
        c += "\n" + novas_rotas
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] Rotas do Comparativo de Despesas adicionadas!")
else:
    print("[AVISO] Rotas já existem.")
