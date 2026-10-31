import re

# Lê o arquivo
c = open('main.py', encoding='utf-8-sig').read()

# O código novo e perfeito das duas rotas
novas_rotas = r'''
@app.get("/custo_pessoal_pdf_completo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_completo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_completo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    # Substitui o texto descritivo
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    # Substitui o valor na coluna % da RCL
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/custo_pessoal_pdf_resumo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_resumo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_resumo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    # Substitui o texto descritivo
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    # Substitui o valor na coluna % da RCL
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

'''

# 1. Remove as funções antigas (do @app.get até o return)
padrao_remover = r'@app\.get\("/custo_pessoal_pdf_completo".*?return HTMLResponse\(.*?\)\s*@app\.get\("/custo_pessoal_pdf_resumo".*?return HTMLResponse\(.*?\)'
c = re.sub(padrao_remover, "", c, flags=re.DOTALL)

# 2. Se não removeu (porque o texto está diferente), remove os defs órfãos
padrao_orfao = r'(?s)(def serve_custo_pessoal_pdf_completo.*?(?=\n@app\.get|\Z))|(def serve_custo_pessoal_pdf_resumo.*?(?=\n@app\.get|\Z))'
c = re.sub(padrao_orfao, "", c)

# 3. Insere as novas rotas no final do arquivo (antes do if __name__ == "__main__")
if 'if __name__ == "__main__":' in c:
    c = c.replace('if __name__ == "__main__":', novas_rotas + '\nif __name__ == "__main__":')
else:
    c += "\n" + novas_rotas

# Salva sem BOM
open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rotas do PDF recriadas do zero!')
