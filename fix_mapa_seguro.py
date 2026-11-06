import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_seguro_{ts}")
c = open(arquivo, encoding='utf-8').read()

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
                    
                    // Tipos que têm tela com histórico (abre a tela)
                    const rotasTela = {
                        'CENTRO_CUSTOS': '/analise_centro_custos',
                        'COMPARATIVO_DESPESAS': '/analise_comparativo_despesas',
                        'COMPARATIVO_RECEITAS': '/analise_comparativo_receitas',
                        'CUSTO_PESSOAL': '/analise_custo_pessoal'
                    };
                    
                    if (rotasTela.hasOwnProperty(tipoUpper)) {
                        // Abre a tela para selecionar o histórico e gerar o PDF
                        window.open(rotasTela[tipoUpper], '_blank');
                    } else {
                        // Tipos que têm PDF direto via FPDF (Balanços, Balancete, DFC, DVP, DMPL)
                        window.open('/download/pdf/' + tipo, '_blank');
                    }
                }"""

c = c[:inicio] + nova_funcao + c[fim:]
open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Função gerarPdfLista ajustada com mapeamento seguro!")
print("-> BALANCETE, BALANCO_*, DFC, DVP, DMPL: PDF direto via /download/pdf/")
print("-> CENTRO_CUSTOS, COMPARATIVO_DESPESAS, COMPARATIVO_RECEITAS, CUSTO_PESSOAL: abre a tela")
