import shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_comp_desp_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Substitui a função gerarPdfLista para redirecionar COMPARATIVO_DESPESAS para a tela correta
antigo = """function gerarPdfLista(nomeArquivo) {
                    let tipo = nomeArquivo.replace('.csv', '');
                    tipo = tipo.replace(/_[0-9]{4}_[A-Z]+_[0-9]+$/, '');
                    window.open('/download/pdf/' + tipo, '_blank');
                }"""

novo = """function gerarPdfLista(nomeArquivo) {
                    // Extrai o tipo do nome do arquivo
                    let tipo = nomeArquivo.replace('.csv', '');
                    tipo = tipo.replace(/_[0-9]{4}_[A-Z]+_[0-9]+$/, '');
                    
                    // COMPARATIVO_DESPESAS tem tela própria (Playwright)
                    if (tipo.toUpperCase().includes('COMPARATIVO_DESPESAS')) {
                        window.open('/analise_comparativo_despesas', '_blank');
                        return;
                    }
                    
                    // Para os demais, usa a rota de PDF via FPDF
                    window.open('/download/pdf/' + tipo, '_blank');
                }"""

if antigo in c:
    c = c.replace(antigo, novo)
    print("[OK] Função gerarPdfLista corrigida para redirecionar COMPARATIVO_DESPESAS")
else:
    print("[AVISO] Função não encontrada no formato exato. Tentando variação...")
    # Tenta variação
    c = c.replace(
        "window.open('/download/pdf/' + tipo, '_blank');",
        """if (tipo.toUpperCase().includes('COMPARATIVO_DESPESAS')) {
                        window.open('/analise_comparativo_despesas', '_blank');
                    } else {
                        window.open('/download/pdf/' + tipo, '_blank');
                    }"""
    )
    print("[OK] Ajuste via variação aplicado")

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] index.html salvo")
