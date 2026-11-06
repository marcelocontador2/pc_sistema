import os, shutil, sys, datetime

ARQUIVO = r"pc_backend\main.py"
BACKUP = f"pc_backend\\main_backup_liquidez_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

# ---------- 1) Backup ----------
shutil.copy2(ARQUIVO, BACKUP)
print(f"[OK] Backup: {BACKUP}")

with open(ARQUIVO, "r", encoding="utf-8") as f:
    linhas = f.readlines()

# ---------- 2) Localizar bloco de _calc_liquidez ----------
inicio = None
for i, l in enumerate(linhas):
    if l.startswith("def _calc_liquidez(periodo)"):
        inicio = i
        break

if inicio is None:
    print("[ERRO] Nao achei 'def _calc_liquidez(periodo):' no main.py")
    sys.exit(1)

fim = len(linhas)
for j in range(inicio + 1, len(linhas)):
    s = linhas[j]
    if s.strip() and not s[0].isspace() and not s.lstrip().startswith("#"):
        fim = j
        break

print(f"[OK] _calc_liquidez ocupa linhas {inicio+1}..{fim} (sera substituida)")

# ---------- 3) Nova _calc_liquidez ----------
NOVA_FUNCAO = r'''def _calc_liquidez(periodo):
    """Calcula indices de liquidez e estrutura a partir do Balanco Patrimonial."""
    from matriz_integridade import _ler_linhas, _get_csv, _limpar_valor
    caminho_bp = _get_csv("BALANCO_PATRIMONIAL", periodo)
    if not caminho_bp:
        return None
    l_bp = _ler_linhas(caminho_bp)

    def buscar(*termos):
        """Retorna o primeiro valor > 0 encontrado para qualquer um dos termos (col 0=Ativo, 3=Passivo)."""
        for termo in termos:
            termo_upper = termo.upper()
            for p in l_bp:
                for col_espec in (0, 3):
                    if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except Exception:
                                pass
        return 0.0

    caixa = buscar("CAIXA E EQUIVALENTES", "DISPONIBILIDADES", "CAIXA")
    ativo_circulante = buscar("ATIVO CIRCULANTE")
    estoques = buscar("ESTOQUES")
    realizavel_lp = buscar("REALIZAVEL A LONGO PRAZO", "REALIZAVEL LONGO PRAZO")
    ativo_nao_circulante = buscar("ATIVO NAO CIRCULANTE", "ATIVO NAO-CIRCULANTE")
    imobilizado = buscar("IMOBILIZADO")
    passivo_circulante = buscar("PASSIVO CIRCULANTE")
    passivo_nao_circulante = buscar("PASSIVO NAO CIRCULANTE", "PASSIVO NAO-CIRCULANTE")
    passivo_total = buscar("PASSIVO TOTAL", "TOTAL DO PASSIVO")
    ativo_total = buscar("ATIVO TOTAL", "TOTAL DO ATIVO")
    patrimonio_liquido = buscar("PATRIMONIO LIQUIDO", "PATRIMONIO LIQUIDO")

    if not ativo_total and ativo_circulante and ativo_nao_circulante:
        ativo_total = ativo_circulante + ativo_nao_circulante
    if not passivo_total and passivo_circulante and passivo_nao_circulante:
        passivo_total = passivo_circulante + passivo_nao_circulante
    if not patrimonio_liquido and ativo_total and passivo_total:
        patrimonio_liquido = ativo_total - passivo_total

    def div(a, b):
        return (a / b) if b else 0.0

    def pct(a, b):
        return ((a / b) * 100) if b else 0.0

    def fmt(v):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    liq_imediata = div(caixa, passivo_circulante)
    liq_corrente = div(ativo_circulante, passivo_circulante)
    liq_seca = div(ativo_circulante - estoques, passivo_circulante)
    liq_geral = div(ativo_circulante + realizavel_lp, passivo_circulante + passivo_nao_circulante)
    endividamento = pct(passivo_total, ativo_total)
    part_cap_terceiros = pct(passivo_total, patrimonio_liquido)
    imob_pl = pct(imobilizado, patrimonio_liquido)

    return {
        "liquidez": {
            "liquidez_imediata": fmt(liq_imediata),
            "liquidez_corrente": fmt(liq_corrente),
            "liquidez_seca": fmt(liq_seca),
            "liquidez_geral": fmt(liq_geral),
        },
        "estrutura": {
            "endividamento_geral": fmt(endividamento),
            "part_capital_terceiros": fmt(part_cap_terceiros),
            "imobilizacao_pl": fmt(imob_pl),
        },
        "valores": {
            "caixa": caixa,
            "ativo_circulante": ativo_circulante,
            "estoques": estoques,
            "realizavel_lp": realizavel_lp,
            "ativo_nao_circulante": ativo_nao_circulante,
            "imobilizado": imobilizado,
            "passivo_circulante": passivo_circulante,
            "passivo_nao_circulante": passivo_nao_circulante,
            "passivo_total": passivo_total,
            "ativo_total": ativo_total,
            "patrimonio_liquido": patrimonio_liquido,
        },
    }


'''

novo_bloco = [NOVA_FUNCAO]
linhas_final = linhas[:inicio] + novo_bloco + linhas[fim:]

# ---------- 4) Anexar as 6 rotas no final ----------
ROTAS = r'''

# =========================================================
# ROTAS DE LIQUIDEZ (adicionadas automaticamente)
# =========================================================

@app.get("/api/calcular_liquidez/{periodo}")
async def api_calcular_liquidez(periodo: str):
    dados = _calc_liquidez(periodo)
    if not dados:
        return {"erro": True, "mensagem": "Balanco Patrimonial nao encontrado para este periodo."}
    return dados


@app.post("/salvar_liquidez/{periodo}")
async def salvar_liquidez_rota(periodo: str):
    try:
        dados = _calc_liquidez(periodo)
        if not dados:
            return {"erro": True, "mensagem": "Sem dados para salvar."}
        import sqlite3 as _sq, json as _js, datetime as _dt
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = _sq.connect(db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
            id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
        data_agora = _dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur.execute("INSERT INTO historico_liquidez (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                    (periodo, data_agora, _js.dumps(dados, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return {"ok": True, "mensagem": "Liquidez salva com sucesso!"}
    except Exception as e:
        return {"erro": True, "mensagem": str(e)}


@app.get("/historico_liquidez")
async def listar_historico_liquidez():
    import sqlite3 as _sq
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_liquidez (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    cur.execute("SELECT id, periodo, data_geracao FROM historico_liquidez ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]


@app.get("/historico_liquidez/{id}")
async def get_liquidez_id(id: int):
    import sqlite3 as _sq, json as _js
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"erro": True, "mensagem": "Nao encontrado"}
    dados = _js.loads(row[2])
    dados["_periodo_hist"] = row[0]
    dados["_data_hist"] = row[1]
    return dados


@app.delete("/excluir_liquidez/{id}")
async def excluir_liquidez(id: int):
    import sqlite3 as _sq
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_liquidez WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/gerar_pdf_liquidez/{id}")
def gerar_pdf_liquidez(id: int):
    import sqlite3 as _sq, json as _js
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fastapi.responses import Response

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = _sq.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT periodo, data_geracao, resultado_json FROM historico_liquidez WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    dados = _js.loads(res_json)
    liq = dados.get("liquidez", {})
    est = dados.get("estrutura", {})
    val = dados.get("valores", {})

    def fmt_moeda(v):
        try:
            return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(v)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 15, "INDICES DE LIQUIDEZ E ESTRUTURA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.ln(4)
    pdf.cell(0, 6, f"Periodo: {periodo.replace('-', ' ')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"Data de Geracao: {data_geracao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "1. INDICES DE LIQUIDEZ", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for label, chave in [
        ("Liquidez Imediata", "liquidez_imediata"),
        ("Liquidez Corrente", "liquidez_corrente"),
        ("Liquidez Seca", "liquidez_seca"),
        ("Liquidez Geral", "liquidez_geral"),
    ]:
        pdf.cell(110, 7, label, border=1)
        pdf.cell(0, 7, str(liq.get(chave, "0,00")), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "2. ESTRUTURA PATRIMONIAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for label, chave in [
        ("Endividamento Geral (%)", "endividamento_geral"),
        ("Part. Capital de Terceiros (%)", "part_capital_terceiros"),
        ("Imobilizacao do PL (%)", "imobilizacao_pl"),
    ]:
        pdf.cell(110, 7, label, border=1)
        pdf.cell(0, 7, str(est.get(chave, "0,00")) + "%", border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(0, 86, 179)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "3. VALORES BASE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for label, chave in [
        ("Caixa e Equivalentes", "caixa"),
        ("Ativo Circulante", "ativo_circulante"),
        ("Estoques", "estoques"),
        ("Realizavel a Longo Prazo", "realizavel_lp"),
        ("Imobilizado", "imobilizado"),
        ("Passivo Circulante", "passivo_circulante"),
        ("Passivo Nao Circulante", "passivo_nao_circulante"),
        ("Passivo Total", "passivo_total"),
        ("Ativo Total", "ativo_total"),
        ("Patrimonio Liquido", "patrimonio_liquido"),
    ]:
        pdf.cell(110, 7, label, border=1)
        pdf.cell(0, 7, fmt_moeda(val.get(chave, 0)), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=liquidez_{id}.pdf"},
    )
# =========================================================
# FIM DAS ROTAS DE LIQUIDEZ
# =========================================================
'''

# Garante que o arquivo termina com quebra de linha antes de anexar
if not linhas_final[-1].endswith("\n"):
    linhas_final[-1] = linhas_final[-1] + "\n"

conteudo_final = "".join(linhas_final) + ROTAS

# ---------- 5) Validar sintaxe antes de escrever ----------
try:
    compile(conteudo_final, ARQUIVO, "exec")
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    print("Nada foi gravado. Backup intacto.")
    sys.exit(1)

# ---------- 6) Gravar ----------
with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(conteudo_final)

print(f"[OK] main.py atualizado ({len(conteudo_final):,} chars)")
print("[OK] Rotas adicionadas:")
print("      GET    /api/calcular_liquidez/{periodo}")
print("      POST   /salvar_liquidez/{periodo}")
print("      GET    /historico_liquidez")
print("      GET    /historico_liquidez/{id}")
print("      DELETE /excluir_liquidez/{id}")
print("      GET    /gerar_pdf_liquidez/{id}")
print()
print("=== PROXIMO PASSO ===")
print("1. PARE o servidor (Ctrl+C)")
print("2. Inicie novamente:  .\\pc_venv\\Scripts\\python.exe -m uvicorn pc_backend.main:app --reload --port 9994")
print("3. Teste: http://127.0.0.1:9994/api/calcular_liquidez/2026-TRIMESTRE-3")
print("4. Abra:  http://127.0.0.1:9994/liquidez   (Ctrl+Shift+R)")
