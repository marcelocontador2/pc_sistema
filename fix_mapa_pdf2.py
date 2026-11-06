import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_mapa2_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Localiza a função gerarPdfLista
inicio = c.find('function gerarPdfLista')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
    exit(1)

idx_chave = c.find('{', inicio)
nivel = 1
i = idx_chave + 1
while nivel > 0 and i < len(c):
    if c[i] == '{': nivel += 1
    elif c[i] == '}': nivel -= 1
    i += 1

fim = i

nova_funcao = """function gerarPdfLista(nomeArquivo) {
                    // Extrai o tipo do nome do arquivo
                    let tipo = nomeArquivo.replace('.csv', '');
                    tipo = tipo.replace(/_[0-9]{4}_[A-Z]+_[0-9]+$/, '');
                    let tipoUpper = tipo.toUpperCase();
                    
                    // Mapeamento: rotas que geram PDF via Playwright (sem abrir tela)
                    const rotasPdf = {
                        'COMPARATIVO_DESPESAS': '/gerar_pdf_comparativo_despesas',
                        'COMPARATIVO_RECEITAS': '/gerar_pdf_comparativo_receitas'
                    };
                    
                    // Mapeamento: tipos que precisam abrir a tela (para selecionar histórico)
                    const rotasTela = {
                        'CENTRO_CUSTOS': '/analise_centro_custos',
                        'CUSTO_PESSOAL': '/analise_custo_pessoal',
                        'COMPOSICAO_RECEITAS_DESPESAS': '/composicao_receitas_despesas',
                        'LIQUIDEZ': '/liquidez_nova',
                        'PANORAMA': '/panorama'
                    };
                    
                    if (rotasPdf.hasOwnProperty(tipoUpper)) {
                        window.open(rotasPdf[tipoUpper], '_blank');
                    } else if (rotasTela.hasOwnProperty(tipoUpper)) {
                        window.open(rotasTela[tipoUpper], '_blank');
                    } else {
                        // FPDF (BALANCO_*, BALANCETE, DFC, DVP, DMPL)
                        window.open('/download/pdf/' + tipo, '_blank');
                    }
                }"""

c = c[:inicio] + nova_funcao + c[fim:]
open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Função gerarPdfLista corrigida!")
print("-> COMPARATIVO_DESPESAS: PDF direto via Playwright")
print("-> COMPARATIVO_RECEITAS: PDF direto via Playwright")
print("-> CENTRO_CUSTOS: abre a tela de Análise por Centro de Custos")
print("-> Demais tipos: PDF via FPDF")
