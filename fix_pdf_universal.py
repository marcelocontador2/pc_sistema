import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. CORRIGIR O BACKEND (main.py)
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_fix_pdf_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# --- Despesas ---
def fix_backend_route(codigo, rota_func, html_relatorio):
    # Encontra a definição da função e substitui a assinatura para aceitar historico_id
    padrao_def = rf'def {rota_func}\([^\)]*\):'
    nova_def = f'def {rota_func}(periodo_atual: str = "2026-TRIMESTRE-3", historico_id: int = None):'
    codigo = re.sub(padrao_def, nova_def, codigo, count=1)
    
    # Encontra a definição da URL e substitui pela lógica condicional
    padrao_url = rf'url = f"http:\/\/127\.0\.0\.1:9994\/{html_relatorio}\?periodo_atual=.*?"'
    nova_url = f'''if historico_id:
        url = f"http://127.0.0.1:9994/{html_relatorio}?historico_id={{historico_id}}&_t={{int(time.time())}}"
    else:
        url = f"http://127.0.0.1:9994/{html_relatorio}?periodo_atual={{periodo_atual}}&_t={{int(time.time())}}"'''
    
    codigo = re.sub(padrao_url, nova_url, codigo, count=1)
    return codigo

c_back = fix_backend_route(c_back, "gerar_pdf_comparativo_despesas", "relatorio_comparativo_despesas_v2")
c_back = fix_backend_route(c_back, "gerar_pdf_comparativo_receitas", "relatorio_comparativo_receitas_v2")

open(back_path, 'w', encoding='utf-8').write(c_back)
print("[OK] Backend corrigido com sucesso (Receitas e Despesas)!")

# ==========================================
# 2. CORRIGIR O FRONTEND (Despesas e Receitas)
# ==========================================
def fix_frontend(arquivo, rota_pdf):
    path = os.path.join("pc_frontend", arquivo)
    if not os.path.exists(path): return
    
    shutil.copy2(path, f"{path}.bak_fix_pdf_{ts}")
    c = open(path, encoding='utf-8').read()

    # Garante que o botão chama a função
    c = c.replace('onclick="window.print()"', 'onclick="gerarPDF()"')
    
    # Remove qualquer lixo da função gerarPDF antiga
    c = re.sub(r'function gerarPDF\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)
    c = re.sub(r'function gerarPDF\(\) \{.*?\n        \}', '', c, flags=re.DOTALL) # Roda 2x por segurança
    
    # Nova função blindada (usa window.location em vez de window.open)
    nova_funcao = f"""
        function gerarPDF() {{
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) {{
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }}
            // Redireciona em vez de abrir pop-up (evita bloqueadores)
            window.location.href = `/{rota_pdf}?historico_id=${{sel.value}}`;
        }}
    """
    
    # Insere a função no final do script principal
    if '</script>' in c:
        c = c.replace('</script>', nova_funcao + '\n    </script>', 1) # Substitui apenas o último script
    else:
        c += f"<script>{nova_funcao}</script>"

    open(path, 'w', encoding='utf-8').write(c)
    print(f"[OK] Frontend de {arquivo} corrigido (sem pop-up)!")

fix_frontend("analise_comparativo_despesas.html", "gerar_pdf_comparativo_despesas")
fix_frontend("analise_comparativo_receitas.html", "gerar_pdf_comparativo_receitas")

# ==========================================
# 3. VERIFICAÇÃO DE SINTAXE DO MAIN.PY
# ==========================================
import ast
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada!")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe do main.py quebrada: {e}")
