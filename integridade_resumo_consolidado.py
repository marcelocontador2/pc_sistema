import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_integridade_resumo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# Localiza a função gerar_pdf_relatorio_consolidado
idx_rota = codigo.find("def gerar_pdf_relatorio_consolidado")
if idx_rota == -1:
    print("[ERRO] Rota do PDF consolidado não encontrada.")
    exit()

fim_rota = codigo.find("\n@app.", idx_rota)
if fim_rota == -1:
    fim_rota = idx_rota + 8000

bloco = codigo[idx_rota:fim_rota]
bloco_orig = bloco

# =========================================================
# 1. Remover a linha que mapeia "integridade" para o PDF completo
# =========================================================
padrao_integridade = re.compile(
    r'\s*\("integridade",\s*"historico_integridade_matriz",\s*"/gerar_pdf_integridade_matriz/\{p\}",\s*"id"\),',
    re.IGNORECASE
)
if padrao_integridade.search(bloco):
    bloco = padrao_integridade.sub("", bloco)
    print("[OK] Integridade removida do loop de PDFs.")

# =========================================================
# 2. Inserir a página de resumo da Integridade ANTES do loop
# =========================================================
# Encontra a linha "pdfs_gerados = []" ou "writer = PdfWriter()" para inserir antes
padrao_inserir = re.compile(r'(\s*with sync_playwright\(\) as p:)')
match_inserir = padrao_inserir.search(bloco)

if match_inserir:
    # HTML do resumo da integridade
    html_resumo = '''
    # === PÁGINA DE RESUMO DA INTEGRIDADE ===
    integridade_resumo_html = ""
    if "integridade" in modulos:
        d_int = modulos["integridade"].get("dados", {})
        inner_int = d_int.get("dados", d_int) if isinstance(d_int, dict) else {}
        
        total_verif = inner_int.get("total_verificacoes", "—")
        total_ok = inner_int.get("total_ok", "—")
        status = inner_int.get("status", "Verificado")
        inconsistencias = inner_int.get("inconsistencias", [])
        
        # Verifica se tem inconsistências
        tem_inconsistencia = False
        if isinstance(inconsistencias, list) and len(inconsistencias) > 0:
            tem_inconsistencia = True
        elif isinstance(inner_int.get("inconsistencias"), str) and inner_int.get("inconsistencias"):
            tem_inconsistencia = True
        
        # Também verifica os dados (se algum é diferente de OK)
        if isinstance(inner_int, dict):
            for k, v in inner_int.items():
                if isinstance(v, str) and v.strip() not in ("OK", "", "—"):
                    if any(x in v.upper() for x in ("INCONSIST", "ERRO", "FALHA", "DIVERG")):
                        tem_inconsistencia = True
                        break
        
        if tem_inconsistencia:
            cor_fundo = "#fff3cd"
            cor_borda = "#ffc107"
            cor_texto = "#856404"
            icone = "⚠"
            titulo = "Atenção: Inconsistências Encontradas"
        else:
            cor_fundo = "#d4edda"
            cor_borda = "#28a745"
            cor_texto = "#155724"
            icone = "✓"
            titulo = "Integridade Verificada com Sucesso"
        
        integridade_resumo_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
            @page {{ size: A4; margin: 20mm; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            .header {{ background: #003366; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
            .status-box {{ background: {cor_fundo}; border-left: 5px solid {cor_borda}; padding: 25px; margin: 20px 0; color: {cor_texto}; }}
            .status-box h3 {{ margin: 0 0 10px 0; font-size: 20px; }}
            .status-box p {{ margin: 5px 0; font-size: 14px; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }}
            .info-card {{ background: #f4f6f9; padding: 20px; border-radius: 6px; text-align: center; }}
            .info-card .label {{ font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
            .info-card .valor {{ font-size: 28px; font-weight: bold; color: #003366; margin-top: 5px; }}
        </style></head><body>
            <div class="header">INTEGRIDADE ENTRE DEMONSTRAÇÕES</div>
            <div class="status-box">
                <h3>{icone} {titulo}</h3>
                <p>Status: <strong>{status}</strong></p>
                <p>Período: <strong>{periodo}</strong></p>
            </div>
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Total de Verificações</div>
                    <div class="valor">{total_verif}</div>
                </div>
                <div class="info-card">
                    <div class="label">Verificações OK</div>
                    <div class="valor">{total_ok}</div>
                </div>
            </div>
        </body></html>"""

'''
    
    # Insere o HTML antes do "with sync_playwright() as p:"
    bloco = bloco[:match_inserir.start()] + html_resumo + bloco[match_inserir.start():]
    print("[OK] Página de resumo da integridade injetada.")
else:
    print("[AVISO] Não foi possível inserir o resumo da integridade.")

# =========================================================
# 3. Ajustar o loop de PDFs para gerar o resumo da integridade
# =========================================================
# Encontra o ponto onde o PDF é gerado (page.set_content(capa_html, ...))
# e adiciona a geração do resumo da integridade logo depois
padrao_capa = re.compile(
    r'(pdfs_gerados\.append\(capa_pdf\)\s*\n)',
    re.IGNORECASE
)

# Vamos procurar onde o capa_bytes é gerado
padrao_capa_geracao = re.compile(
    r'(capa_bytes\s*=\s*page\.pdf\(format="A4", orientation="landscape", print_background=True, margin=\{"top":"0","bottom":"0","left":"0","right":"0"\}\))',
    re.IGNORECASE
)

match_capa = padrao_capa_geracao.search(bloco)
if match_capa:
    # Adiciona a geração do resumo da integridade logo após a capa
    integridade_geracao = match_capa.group(1) + '''
        # Gera a página de resumo da integridade
        if integridade_resumo_html:
            page.set_content(integridade_resumo_html, wait_until="networkidle")
            page.wait_for_timeout(300)
            integridade_bytes = page.pdf(format="A4", orientation="portrait", print_background=True, margin={"top":"15mm","bottom":"15mm","left":"15mm","right":"15mm"})
            pdfs_gerados.append(integridade_bytes)
            print(f"[OK] Integridade: resumo gerado")
'''
    bloco = bloco.replace(match_capa.group(1), integridade_geracao)
    print("[OK] Geração do resumo da integridade adicionada após a capa.")

# =========================================================
# Substitui o bloco no código
# =========================================================
codigo = codigo.replace(bloco_orig, bloco)

try:
    compile(codigo, arq_main, "exec")
    print("[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"[ERRO SINTAXE] linha {e.lineno}: {e.msg}")
    exit()

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] main.py salvo.")
