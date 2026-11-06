import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_nome_fix_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Corrige o botão para usar item.nome (que é o nome do arquivo real)
c = c.replace(
    "onclick=\"gerarPdfLista('${item.arquivo}')\"",
    "onclick=\"gerarPdfLista('${item.nome}')\""
)

# 2. Ajusta a função gerarPdfLista para extrair o tipo corretamente
c = c.replace(
    """function gerarPdfLista(tipoOuArquivo) {
                    // Se for um nome de arquivo (termina com .csv), extrai o tipo completo
                    let tipo = tipoOuArquivo;
                    if (tipoOuArquivo.endsWith('.csv')) {
                        // Remove o .csv e a parte do período (ex: _2026_TRIMESTRE_3)
                        tipo = tipoOuArquivo.replace('.csv', '').replace(/_\\d{4}_[A-Z]+_\\d+$/, '');
                    }
                    window.open('/download/pdf/' + tipo, '_blank');
                }""",
    """function gerarPdfLista(nomeArquivo) {
                    // Extrai o tipo do nome do arquivo:
                    // BALANCO_ORCAMENTARIO_2026_TRIMESTRE_3.csv -> BALANCO_ORCAMENTARIO
                    // BALANCETE_2026_TRIMESTRE_3.csv -> BALANCETE
                    let tipo = nomeArquivo.replace('.csv', '');
                    // Remove o sufixo do período (ex: _2026_TRIMESTRE_3)
                    tipo = tipo.replace(/_[0-9]{4}_[A-Z]+_[0-9]+$/, '');
                    window.open('/download/pdf/' + tipo, '_blank');
                }"""
)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] index.html corrigido!")

# 3. Confirma se o botão agora usa item.nome
if "gerarPdfLista('${item.nome}')" in c:
    print("[OK] Botão agora usa item.nome (nome real do arquivo)")
else:
    print("[AVISO] Substituição não aplicada, verifique manualmente")

# 4. Mostra o trecho da função corrigida
idx = c.find('gerarPdfLista(nomeArquivo)')
if idx != -1:
    print("\n--- FUNÇÃO CORRIGIDA ---")
    print(c[idx:idx+500])

# 5. Valida sintaxe (aqui não tem como validar JS, só confirmar a estrutura)
