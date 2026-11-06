import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\index.html"

shutil.copy2(arquivo, f"{arquivo}.bak_mapeamento_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Corrige a função gerarPdfLista para extrair o tipo do nome do arquivo
c = c.replace(
    "function gerarPdfLista(tipo) { window.open('/download/pdf/' + tipo, '_blank'); }",
    """function gerarPdfLista(tipoOuArquivo) {
                    // Se for um nome de arquivo (termina com .csv), extrai o tipo completo
                    let tipo = tipoOuArquivo;
                    if (tipoOuArquivo.endsWith('.csv')) {
                        // Remove o .csv e a parte do período (ex: _2026_TRIMESTRE_3)
                        tipo = tipoOuArquivo.replace('.csv', '').replace(/_\d{4}_[A-Z]+_\d+$/, '');
                    }
                    window.open('/download/pdf/' + tipo, '_blank');
                }"""
)

# 2. Corrige a chamada do botão para passar o nome do arquivo em vez do tipo genérico
# Procura o botão "PDF" na tabela e muda o parâmetro
c = c.replace(
    "onclick=\"gerarPdfLista('${item.tipo}')\"",
    "onclick=\"gerarPdfLista('${item.arquivo}')\""
)
c = c.replace(
    "onclick=\"gerarPdfLista('${r.tipo}')\"",
    "onclick=\"gerarPdfLista('${r.arquivo}')\""
)

# 3. Verifica se a tabela usa 'item.tipo' ou 'r.tipo' e mostra o contexto
idx = c.find('gerarPdfLista')
if idx != -1:
    print("--- CONTEXTO DO BOTÃO ---")
    print(c[max(0,idx-500):idx+500])

open(arquivo, 'w', encoding='utf-8').write(c)
print("\n[OK] index.html corrigido!")
print("-> Botão PDF agora passa o nome do arquivo (ex: BALANCO_ORCAMENTARIO_2026_TRIMESTRE_3.csv)")
print("-> A função gerarPdfLista extrai o tipo específico (BALANCO_ORCAMENTARIO) e chama a rota correta")

# 4. Verifica como o backend recebe o tipo e escolhe o layout
print("\n--- VERIFICANDO BACKEND ---")
c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
match = re.search(r'def download_pdf\(tipo: str.*?\n(.*?)(?=\n@app\.|\Z)', c_back, re.DOTALL)
if match:
    corpo = match.group(1)
    # Verifica se o backend diferencia BALANCO_ORCAMENTARIO de BALANCO
    if 'BALANCO_ORCAMENTARIO' in corpo:
        print("[OK] Backend tem lógica para BALANCO_ORCAMENTARIO")
    else:
        print("[AVISO] Backend NÃO tem lógica específica para BALANCO_ORCAMENTARIO")
    
    if 'elif tipo == "BALANCO_PATRIMONIAL"' in corpo:
        print("[OK] Backend tem lógica para BALANCO_PATRIMONIAL")
    else:
        print("[AVISO] Backend NÃO tem lógica para BALANCO_PATRIMONIAL")
