import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_front_pdfcsv_{ts}")
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
                    
                    // Tipos que usam a rota /download/pdf_csv/ (PDF direto do CSV)
                    const tiposCsv = ['COMPARATIVO_DESPESAS', 'COMPARATIVO_RECEITAS', 'CENTRO_CUSTOS'];
                    
                    if (tiposCsv.includes(tipoUpper)) {
                        window.open('/download/pdf_csv/' + tipo, '_blank');
                    } else {
                        window.open('/download/pdf/' + tipo, '_blank');
                    }
                }"""

c = c[:inicio] + nova_funcao + c[fim:]
open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Função gerarPdfLista atualizada para usar /download/pdf_csv/ nos tipos comparativos e centro de custos.")
