from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Verificar se a funcao api_custo_pessoal ja le a config
if 'def api_custo_pessoal(periodo: str, entidade: str = None):' in conteudo:
    print("AVISO: api_custo_pessoal ja foi atualizada (entidade=None)")
else:
    # 2. Substituir a assinatura
    trecho_antigo = 'async def api_custo_pessoal(periodo: str, entidade: str = "COFEN"):'
    trecho_novo = 'async def api_custo_pessoal(periodo: str, entidade: str = None):'
    if trecho_antigo in conteudo:
        conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
        print("OK: Assinatura atualizada (entidade=None)")
    else:
        print("AVISO: nao achei a assinatura original")

    # 3. Adicionar a leitura da configuracao no inicio da funcao
    # Encontrar a linha "import re, os" (dentro da funcao)
    trecho_import = '    import re, os'
    if trecho_import in conteudo:
        # Adicionar a leitura da config DEPOIS do import
        novo_import = '''    import re, os
    import sqlite3 as _sqlite3
    # Ler configuracao global
    if not entidade:
        _db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        _conn = _sqlite3.connect(_db_path)
        _cur = _conn.cursor()
        _cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
        _row = _cur.fetchone()
        _conn.close()
        entidade = _row[0] if _row else "COFEN"
    print(f"[CUSTO PESSOAL] entidade={entidade}")'''
        conteudo = conteudo.replace(trecho_import, novo_import, 1)
        print("OK: Leitura da configuracao adicionada")
    else:
        print("AVISO: nao achei o import 're, os'")

    # 4. Validar sintaxe
    try:
        ast.parse(conteudo)
        print("Sintaxe OK!")
    except SyntaxError as e:
        print(f"ERRO de sintaxe: {e}")
        exit(1)

    arquivo.write_text(conteudo, encoding="utf-8")
    print("OK: main.py atualizado!")

print("\nCommit 2 concluido!")
