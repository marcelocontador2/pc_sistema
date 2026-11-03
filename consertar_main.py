import os, glob, shutil, ast

back_dir = r"pc_backend"
backups = glob.glob(os.path.join(back_dir, "main.py.bak_lote_*"))
backups.sort(reverse=True)

if not backups:
    print("[ERRO] Nenhum backup .bak_lote_ encontrado!")
    exit(1)

ultimo_backup = backups[0]
print(f"Restaurando o backup: {ultimo_backup}")
shutil.copy2(ultimo_backup, os.path.join(back_dir, "main.py"))

back_path = os.path.join(back_dir, "main.py")
c_back = open(back_path, encoding='utf-8-sig').read()

telas = [
    {"rota": "gerar_pdf_custo_pessoal", "relatorio": "relatorio_custo_pessoal"},
    {"rota": "gerar_pdf_analise_financeira_bf", "relatorio": "relatorio_analise_financeira_bf"},
    {"rota": "gerar_pdf_analise_orcamentaria", "relatorio": "relatorio_analise_orcamentaria"},
    {"rota": "gerar_pdf_analise_patrimonial", "relatorio": "relatorio_analise_patrimonial"},
    {"rota": "gerar_pdf_composicao_receitas_despesas", "relatorio": "relatorio_composicao_receitas_despesas"}
]

for t in telas:
    # 1. Mudar a assinatura da função (com replace simples)
    assinatura_antiga = f'def {t["rota"]}(periodo_atual: str = "2026-TRIMESTRE-3"):'
    assinatura_nova = f'def {t["rota"]}(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):'
    c_back = c_back.replace(assinatura_antiga, assinatura_nova)

    # 2. Mudar a URL do Playwright (Substituição em bloco com quebra de linha)
    # O código original tem 4 espaços de indentação
    url_antiga = f'    url = f"http://127.0.0.1:9994/{t["relatorio"]}?periodo_atual={{periodo_atual}}&_t={{int(time.time())}}"'
    url_nova = f'''    if historico_id:
        url = f"http://127.0.0.1:9994/{t["relatorio"]}?historico_id={{historico_id}}&_t={{int(time.time())}}"
    else:
        url = f"http://127.0.0.1:9994/{t["relatorio"]}?periodo_atual={{periodo_atual}}&_t={{int(time.time())}}"'''
    
    c_back = c_back.replace(url_antiga, url_nova)

open(back_path, 'w', encoding='utf-8').write(c_back)

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py consertada e 100% validada!")
except SyntaxError as e:
    print(f"[ERRO] Ainda há um erro de sintaxe: {e}")
    # Se ainda der erro, é porque o nome do parâmetro ou a URL estavam ligeiramente diferentes
