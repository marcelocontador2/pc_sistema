import re

arquivo = r"pc_frontend\panorama.html"
with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Adiciona a exportacao para o escopo global logo antes do fechamento do script
if "window.salvarPanorama =" not in html:
    script_fix = """
    // --- Fix para os botoes funcionarem no HTML ---
    window.salvarPanorama = salvarPanorama;
    window.exibirSelecionado = exibirSelecionado;
    window.excluirSelecionado = excluirSelecionado;
    window.gerarPDFPanorama = gerarPDFPanorama;
    // ----------------------------------------------
    """
    
    # Procura o ultimo </script> e insere o fix antes dele
    ultimo_script = html.rfind('</script>')
    if ultimo_script != -1:
        html = html[:ultimo_script] + script_fix + html[ultimo_script:]
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] Funcoes exportadas para o escopo global. Botoes devem funcionar agora.")
    else:
        print("[ERRO] Tag </script> não encontrada.")
else:
    print("[OK] Funcoes já estão no escopo global.")
