import re

c = open('main.py', encoding='utf-8-sig').read()

# 1. Substituir a função do PDF Resumo para injetar o percentual correto
# Primeiro, encontramos a função e substituímos o corpo dela
pattern_resumo = r'(@app\.get\("/custo_pessoal_pdf_resumo", response_class=HTMLResponse\)\s*def serve_custo_pessoal_pdf_resumo\(.*?\):\s*)(.*?)(?=@app\.get|\Z)'

nova_funcao_resumo = r'''\1
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_resumo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Injeção direta baseada na entidade
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
'''

# Aplicar a substituição (com flags DOTALL para pegar múltiplas linhas)
c = re.sub(pattern_resumo, nova_funcao_resumo, c, flags=re.DOTALL)

# 2. Garantir que o parâmetro entidade está na assinatura (se não estiver)
c = c.replace(
    'def serve_custo_pessoal_pdf_resumo():',
    'def serve_custo_pessoal_pdf_resumo(entidade: str = "COFEN"):'
)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rota do PDF Resumo corrigida com injeção de percentual!')
