import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Localiza o inicio da funcao gerar_pdf
inicio = texto.find('def gerar_pdf_relatorio_consolidado(id: int):')
if inicio == -1:
    print("[ERRO] Funcao gerar_pdf nao encontrada.")
    sys.exit(1)

# 2. Localiza a linha que pega o periodo do banco
# (procura por 'periodo = row[0]' ou 'periodo =' dentro da funcao)
fim_trecho = texto.find('\n', inicio)
# Vamos procurar a primeira ocorrencia de "periodo =" dentro da funcao
import re
match = re.search(r'(\n\s+periodo\s*=\s*[^\n]+)', texto[inicio:inicio+3000])
if not match:
    print("[ERRO] Nao achei a linha 'periodo = ...' dentro da funcao.")
    sys.exit(1)

# 3. Insere a normalizacao logo apos a definicao do periodo
posicao_original = inicio + match.start(1)
linha_original = match.group(1)
# Cria a versao normalizada
normalizacao = '''
    # Normaliza o periodo (TRIMESTRAL -> TRIMESTRE)
    periodo_normalizado = str(periodo).replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo_normalizado.upper():
        partes = periodo_normalizado.upper().split("-")
        if len(partes) == 3:
            periodo_normalizado = f"{partes[0]}-TRIMESTRE-{partes[2]}"
    print(f"[PDF] Periodo original: {periodo} -> normalizado: {periodo_normalizado}")
'''
texto = texto[:posicao_original] + linha_original + normalizacao + texto[posicao_original + len(linha_original):]

# 4. Substitui todas as buscas no banco dentro da funcao gerar_pdf para usar periodo_normalizado
inicio_pdf = texto.find('def gerar_pdf_relatorio_consolidado(id: int):')
fim_pdf = texto.find('\n@app', inicio_pdf + 10)
if fim_pdf == -1: fim_pdf = len(texto)

bloco_pdf = texto[inicio_pdf:fim_pdf]
# Substitui as queries que usam %s com periodo
bloco_pdf = bloco_pdf.replace(', (periodo,))', ', (periodo_normalizado,))')
bloco_pdf = bloco_pdf.replace(', (f"%{periodo}%",))', ', (f"%{periodo_normalizado}%",))')
bloco_pdf = bloco_pdf.replace('periodo LIKE %s', 'periodo LIKE %s')
# Tambem corrige o cabecalho do PDF para mostrar o periodo normalizado
bloco_pdf = bloco_pdf.replace('Período: {periodo}', 'Período: {periodo_normalizado}')
bloco_pdf = bloco_pdf.replace('f"Período: {periodo}"', 'f"Período: {periodo_normalizado}"')

texto = texto[:inicio_pdf] + bloco_pdf + texto[fim_pdf:]

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Normalizacao aplicada na funcao gerar_pdf.")
