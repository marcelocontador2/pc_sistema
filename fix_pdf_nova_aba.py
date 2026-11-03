import re, shutil, datetime, os

ts = datetime.datetime.now().strftime('%H%M%S')

def fix_frontend_blank(arquivo, rota_pdf):
    path = os.path.join("pc_frontend", arquivo)
    if not os.path.exists(path): return
    
    shutil.copy2(path, f"{path}.bak_blank_{ts}")
    c = open(path, encoding='utf-8').read()

    # Remove a função gerarPDF antiga
    c = re.sub(r'function gerarPDF\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)
    
    # Nova função usando a técnica do link invisível (não bloqueia pop-up e abre em nova aba)
    nova_funcao = f"""
        function gerarPDF() {{
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) {{
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }}
            
            const url = `/{rota_pdf}?historico_id=${{sel.value}}`;
            
            // Cria um link temporário para abrir em nova aba
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }}
    """
    
    # Insere no final do script
    if '</script>' in c:
        c = c.replace('</script>', nova_funcao + '\n    </script>', 1)
    else:
        c += f"<script>{nova_funcao}</script>"

    open(path, 'w', encoding='utf-8').write(c)
    print(f"[OK] {arquivo} atualizado para abrir PDF em nova aba!")

fix_frontend_blank("analise_comparativo_despesas.html", "gerar_pdf_comparativo_despesas")
fix_frontend_blank("analise_comparativo_receitas.html", "gerar_pdf_comparativo_receitas")
