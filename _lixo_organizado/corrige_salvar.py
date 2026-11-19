import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Localiza a rota que SALVA o relatorio no banco
inicio = texto.find('async def salvar_relatorio_consolidado_novo(periodo: str):')
if inicio == -1:
    print("[ERRO] Rota de salvar nao encontrada.")
    sys.exit(1)

# 2. Insere a normalizacao logo apos a definicao da funcao
posicao_insercao = texto.find('\n', inicio) + 1
normalizacao = '''
    # Normaliza o periodo antes de salvar no banco
    periodo = periodo.replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo.upper():
        partes = periodo.upper().split("-")
        if len(partes) == 3:
            periodo = f"{partes[0]}-TRIMESTRE-{partes[2]}"
    print(f"[SALVAR] Periodo normalizado: {periodo}")
'''
texto = texto[:posicao_insercao] + normalizacao + texto[posicao_insercao:]

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Normalizacao adicionada na rota de SALVAR.")
