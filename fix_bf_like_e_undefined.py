import shutil
import ast

# --- PARTE 1: Corrigir o Backend (busca com LIKE na tabela de BF) ---
print("🔧 CORRIGINDO O BACKEND (main.py)...")

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bf_like")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substitui a linha da query para a tabela de BF, usando LIKE
linha_antiga = 'cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))'
linha_nova = '''# Para a tabela de BF, o período está salvo como "2026-TRIMESTRE-3 vs 2025-TRIMESTRE-3"
                    if chave == "analise_financeira_bf":
                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                    else:
                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))'''

if linha_antiga in conteudo:
    conteudo = conteudo.replace(linha_antiga, linha_nova)
    print("✅ Backend: query de BF ajustada para usar LIKE.")
else:
    print("⚠️ Trecho exato não encontrado. Tentando abordagem alternativa...")
    # Abordagem alternativa: procurar a função e substituir
    idx = conteudo.find('cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))')
    if idx != -1:
        # Substitui a linha inteira
        inicio_linha = conteudo.rfind('\n', 0, idx) + 1
        fim_linha = conteudo.find('\n', idx) + 1
        conteudo = conteudo[:inicio_linha] + '                    # Bypass para BF (período salvo como "2026-TRIMESTRE-3 vs 2025-TRIMESTRE-3")\n                    if chave == "analise_financeira_bf":\n                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))\n                    else:\n                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))\n' + conteudo[fim_linha:]
        print("✅ Backend: query de BF ajustada via abordagem alternativa.")

try:
    ast.parse(conteudo)
    with open(caminho_main, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ main.py salvo e sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")

# --- PARTE 2: Corrigir o Frontend (total_faltando -> faltando.length) ---
print("\n🔧 CORRIGINDO O FRONTEND (relatorio_consolidado.html)...")

caminho_html = "pc_frontend/relatorio_consolidado.html"
shutil.copy(caminho_html, caminho_html + ".bak_fix_total_faltando")

with open(caminho_html, "r", encoding="utf-8") as f:
    html = f.read()

if "${data.total_faltando}" in html:
    html = html.replace("${data.total_faltando}", "${data.faltando ? data.faltando.length : 0}")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Frontend: variável 'total_faltando' substituída por 'faltando.length'.")
else:
    print("⚠️ A variável 'total_faltando' não foi encontrada no HTML.")
