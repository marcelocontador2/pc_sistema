c = open('main.py', encoding='utf-8-sig').read()

# 1. Localizar o início da função (com ou sem entidade)
import re

# Vamos remover tudo entre 'def serve_custo_pessoal_pdf_resumo...' e a próxima rota '@app.get'
pattern = r'(@app\.get\("/custo_pessoal_pdf_resumo", response_class=HTMLResponse\)\s*def serve_custo_pessoal_pdf_resumo\(.*?\):)(.*?)(?=@app\.get|\Z)'

# A nova função correta
nova_funcao = r'''@app.get("/custo_pessoal_pdf_resumo", response_class=HTMLResponse)
def serve_custo_pessoal_pdf_resumo(entidade: str = "COFEN"):
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_frontend", "custo_pessoal_pdf_resumo.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Injeção direta baseada na entidade
    pct = "60,00%" if entidade.upper() == "COREN" else "50,00%"
    html_content = html_content.replace("Limite Resolução Cofen 814/2026 (50% da RCL)", f"Limite Resolução Cofen 814/2026 ({pct} da RCL)")
    html_content = html_content.replace('<td class="right">50,00%</td>', f'<td class="right">{pct}</td>')
    
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

'''

# Substituir
c = re.sub(pattern, nova_funcao, c, flags=re.DOTALL)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] Rota do PDF Resumo corrigida (sem regex quebrado)!')
