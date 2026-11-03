import os, re

front_dir = r"pc_frontend"
arquivos_html = [f for f in os.listdir(front_dir) if f.endswith(".html")]

print(f"{'ARQUIVO':<45} | {'TEM HISTÓRICO?':<15} | {'COMO CHAMA O PDF'}")
print("-" * 100)

for arquivo in sorted(arquivos_html):
    caminho = os.path.join(front_dir, arquivo)
    try:
        html = open(caminho, encoding='utf-8-sig').read()
        
        # 1. Verifica se tem a caixa de histórico
        tem_historico = "name=\"historico\"" in html or "historico-lista" in html
        
        # 2. Verifica como o PDF é chamado
        modo_pdf = "Não tem botão PDF"
        
        if "window.print()" in html:
            modo_pdf = "window.print() (Nativo)"
        
        # Procura chamadas via window.open ou links
        matches = re.findall(r'window\.open\([`\'"](.*?)[`\'"]', html)
        if not matches:
            matches = re.findall(r'href=[`\'"](.*?gerar_pdf.*?)[`\'"]', html)
            
        if matches:
            rota = matches[0]
            # Limpa a rota para mostrar só o endpoint
            if '/gerar_pdf' in rota:
                modo_pdf = f"Rota API: {rota.split('?')[0]}"
                
        # 3. Verifica se tem a função onclick chamando algo de PDF
        if "onclick=\"gerarPDF" in html or "onclick=\"imprimir" in html:
            modo_pdf += " (via função JS)"

        if tem_historico or "PDF" in modo_pdf or "print" in modo_pdf:
            print(f"{arquivo:<45} | {'SIM' if tem_historico else 'NÃO':<15} | {modo_pdf}")

    except Exception as e:
        print(f"Erro ao ler {arquivo}: {e}")
