import shutil
import ast
import re

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_mapa_definitivo")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Substitui a linha que busca no mapa_tabelas por uma busca limpa e forçada
old_mapa_search = '''            tabela, coluna = mapa_tabelas.get(nome_interno, (None, None))'''
new_mapa_search = '''            # --- BUSCA INTELIGENTE NO MAPA_TABELAS ---
            tabela, coluna = mapa_tabelas.get(nome_interno, (None, None))
            if not tabela and "DMPL" in nome_interno:
                tabela, coluna = "historico_analise_dmpl", "resultado_json"
            # ----------------------------------------'''

if old_mapa_search in conteudo:
    conteudo = conteudo.replace(old_mapa_search, new_mapa_search)
    print("✅ Busca no mapa_tabelas corrigida e forçada para o DMPL.")
else:
    print("❌ Linha de busca no mapa_tabelas não encontrada.")

# Vamos também garantir que, se der erro no try/except do DMPL, ele mostre algo em vermelho e não fique em branco
old_except = '''            except Exception as e:
                html_parts.append(f"<p style='color:red;'>Erro ao renderizar mÃ³dulo: {e}</p>")'''
new_except = '''            except Exception as e:
                html_parts.append(f"<p style='color:red;'>Erro ao renderizar módulo: {e}</p>")
                if "DMPL" in nome_interno:
                    import traceback
                    print(f"DEBUG ERRO DMPL: {traceback.format_exc()}")'''

if old_except in conteudo:
    conteudo = conteudo.replace(old_except, new_except)
    print("✅ Tratamento de erro do DMPL ajustado para mostrar detalhes no terminal.")
else:
    print("⚠️ Bloco 'except' genérico não encontrado, mas seguiremos em frente.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
