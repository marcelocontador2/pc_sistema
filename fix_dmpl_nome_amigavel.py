import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_nome_amigavel")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# --- Correção 1: mapa_tabelas — adiciona entrada com o nome amigável do DMPL
old_mapa = '"DMPL": ("historico_analise_dmpl", "resultado_json"),'
new_mapa = '"DMPL": ("historico_analise_dmpl", "resultado_json"),\n        "Demonstração das Mutações do PL (DMPL)": ("historico_analise_dmpl", "resultado_json"),'
if old_mapa in conteudo:
    conteudo = conteudo.replace(old_mapa, new_mapa)
    print("✅ mapa_tabelas: entrada adicional 'Demonstração das Mutações do PL (DMPL)' criada.")
else:
    print("⚠️ mapa_tabelas: entrada 'DMPL' não encontrada no formato esperado.")

# --- Correção 2: ordem_modelo — troca a chave 'DMPL' pelo nome amigável
old_ordem = '("DMPL", "7. DemonstraÃ§Ã£o das MutaÃ§Ãµes do PatrimÃ´nio LÃquido (DMPL)"),'
new_ordem = '("Demonstração das Mutações do PL (DMPL)", "7. DemonstraÃ§Ã£o das MutaÃ§Ãµes do PatrimÃ´nio LÃquido (DMPL)"),'
if old_ordem in conteudo:
    conteudo = conteudo.replace(old_ordem, new_ordem)
    print("✅ ordem_modelo: chave trocada para 'Demonstração das Mutações do PL (DMPL)'.")
else:
    print("⚠️ ordem_modelo: linha do DMPL não encontrada no formato esperado.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
