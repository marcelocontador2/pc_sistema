import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_mapa_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Localiza a função gerarPdfLista e substitui inteira
inicio = c.find('function gerarPdfLista')
if inicio == -1:
    print("[ERRO] Função não encontrada.")
    exit(1)

# Encontra o fim da função (próximo '}' de fechamento)
idx_chave = c.find('{', inicio)
nivel = 1
i = idx_chave + 1
while nivel > 0 and i < len(c):
    if c[i] == '{': nivel += 1
    elif c[i] == '}': nivel -= 1
    i += 1

fim = i

nova_funcao = """function gerarPdfLista(nomeArquivo) {
                    // Extrai o tipo do nome do arquivo (ex: BALANCO_ORCAMENTARIO_2026_TRIMESTRE_3.csv -> BALANCO_ORCAMENTARIO)
                    let tipo = nomeArquivo.replace('.csv', '');
                    tipo = tipo.replace(/_[0-9]{4}_[A-Z]+_[0-9]+$/, '');
                    let tipoUpper = tipo.toUpperCase();
                    
                    // Mapeamento: tipos que têm rota própria via Playwright
                    const rotasEspeciais = {
                        'COMPARATIVO_DESPESAS': '/gerar_pdf_comparativo_despesas',
                        'COMPARATIVO_RECEITAS': '/gerar_pdf_comparativo_receitas',
                        'CENTRO_CUSTOS': null,
                        'CUSTO_PESSOAL': '/gerar_pdf_custo_pessoal',
                        'ANALISE_PATRIMONIAL': '/gerar_pdf_analise_patrimonial',
                        'ANALISE_ORCAMENTARIA': '/gerar_pdf_analise_orcamentaria',
                        'LIQUIDEZ': '/gerar_pdf_liquidez',
                        'PANORAMA': '/gerar_pdf_panorama',
                        'COMPOSICAO_RECEITAS_DESPESAS': '/gerar_pdf_composicao_receitas_despesas'
                    };
                    
                    if (rotasEspeciais.hasOwnProperty(tipoUpper)) {
                        let rota = rotasEspeciais[tipoUpper];
                        if (rota) {
                            window.open(rota, '_blank');
                        } else {
                            alert('Este tipo de relatório não tem PDF disponível na lista.');
                        }
                        return;
                    }
                    
                    // Para os demais, usa a rota FPDF /download/pdf/{tipo}
                    window.open('/download/pdf/' + tipo, '_blank');
                }"""

c = c[:inicio] + nova_funcao + c[fim:]
open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Função gerarPdfLista substituída com mapeamento completo!")
print("-> COMPARATIVO_DESPESAS → /gerar_pdf_comparativo_despesas")
print("-> COMPARATIVO_RECEITAS → /gerar_pdf_comparativo_receitas")
print("-> BALANCO_*, BALANCETE, DFC, DVP, DMPL → /download/pdf/{tipo}")
