from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Corrigir a rota do PDF completo
trecho_antigo = '''@app.get("/gerar_pdf_completo_custo_pessoal")
def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3"):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os
        
        # Se um ID de historico foi passado, buscar o periodo correto
        if id:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            conn.close()
            if row:
                periodo = row[0]
                print(f"[PDF COMPLETO] Historico ID {id} -> periodo {periodo}")'''

trecho_novo = '''@app.get("/gerar_pdf_completo_custo_pessoal")
def gerar_pdf_completo_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Se um ID de historico foi passado, buscar o periodo correto
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF COMPLETO] Historico ID {id} -> periodo {periodo}")
        
        # Buscar entidade da configuracao (se nao foi passada)
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        
        conn.close()
        print(f"[PDF COMPLETO] periodo={periodo}, entidade={entidade}")'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Rota do PDF completo corrigida (busca entidade da config)!")

# 2. Corrigir a rota do PDF resumo
trecho_antigo2 = '''@app.get("/gerar_pdf_custo_pessoal")
def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3"):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os
        
        # Se um ID de historico foi passado, buscar o periodo correto
        if id:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            conn.close()
            if row:
                periodo = row[0]
                print(f"[PDF RESUMO] Historico ID {id} -> periodo {periodo}")'''

trecho_novo2 = '''@app.get("/gerar_pdf_custo_pessoal")
def gerar_pdf_custo_pessoal(id: int = None, periodo: str = "2026-TRIMESTRE-3", entidade: str = None):
    try:
        from playwright.sync_api import sync_playwright
        import sqlite3, os
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Se um ID de historico foi passado, buscar o periodo correto
        if id:
            cur.execute("SELECT periodo FROM historico_custo_pessoal WHERE id = ?", (id,))
            row = cur.fetchone()
            if row:
                periodo = row[0]
                print(f"[PDF RESUMO] Historico ID {id} -> periodo {periodo}")
        
        # Buscar entidade da configuracao (se nao foi passada)
        if not entidade:
            cur.execute("SELECT valor FROM configuracoes WHERE chave = 'tipo_entidade'")
            row = cur.fetchone()
            entidade = row[0] if row else "COFEN"
        
        conn.close()
        print(f"[PDF RESUMO] periodo={periodo}, entidade={entidade}")'''

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: Rota do PDF resumo corrigida (busca entidade da config)!")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
