import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_rota_template_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Remove rota antiga se existir
padrao_antigo = re.compile(
    r'@app\.get\("/gerar_pdf_relatorio_consolidado/\{id\}"\).*?(?=\n@app\.|\Z)',
    re.DOTALL
)
codigo = padrao_antigo.sub("", codigo)

# =========================================================
# Nova rota — usa o template HTML externo
# =========================================================
nova_rota = r'''
@app.get("/gerar_pdf_relatorio_consolidado/{id}")
def gerar_pdf_relatorio_consolidado(id: int):
    from playwright.sync_api import sync_playwright
    from fastapi.responses import Response
    import sqlite3, json, os

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT periodo, data_geracao, resultado_json FROM historico_relatorio_consolidado WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content="Historico nao encontrado.", status_code=404, media_type="text/plain")

    periodo, data_geracao, res_json = row
    dados = json.loads(res_json).get("dados", {})

    # Le o template HTML
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "relatorio_consolidado_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Serializa o JSON e injeta no template
    # Usa json.dumps com ensure_ascii=False para manter acentos
    dados_json_str = json.dumps(dados, ensure_ascii=False)
    # Escapa "</script>" para evitar quebrar o HTML
    dados_json_str = dados_json_str.replace("</", "<\\/")

    html_final = template.replace("{dados_json}", dados_json_str).replace("{periodo}", periodo).replace("{data_geracao}", data_geracao)

    # Renderiza com Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_final, wait_until="networkidle")
        page.wait_for_timeout(1000)
        pdf_bytes = page.pdf(
            format="A4",
            orientation="portrait",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}
        )
        browser.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=relatorio_consolidado_{id}.pdf"}
    )
'''

codigo += "\n" + nova_rota

# Valida sintaxe
try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] Rota do PDF consolidado atualizada para usar o template externo.")
