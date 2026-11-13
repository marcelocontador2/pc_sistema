import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_final_fallback")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Encontra o bloco que verifica se o módulo existe no JSON
old_block = '''            m = modulos_por_nome.get(nome_interno)
            if not m:
                html_parts.append("<div class='page-break'></div>")
                html_parts.append(f"<h2>{titulo_exibicao}</h2>")
                html_parts.append("<p style='color:red;'>MÃ³dulo nÃ£o encontrado nos dados consolidados.</p>")
                continue'''

new_block = '''            m = modulos_por_nome.get(nome_interno)
            
            # --- FALLBACK PARA O DMPL ---
            if not m and "DMPL" in nome_interno:
                # Tenta achar pela chave "DMPL" (nome amigável antigo)
                m = modulos_por_nome.get("DMPL")
                if not m:
                    # Se ainda não achou, força a criação do objeto para buscar no PG
                    m = {"nome": "DMPL", "data_geracao": "N/A"}
                    print("DEBUG: Usando fallback para DMPL no PDF.")
            # ----------------------------
                
            if not m:
                html_parts.append("<div class='page-break'></div>")
                html_parts.append(f"<h2>{titulo_exibicao}</h2>")
                html_parts.append("<p style='color:red;'>MÃ³dulo nÃ£o encontrado nos dados consolidados.</p>")
                continue'''

if old_block in conteudo:
    conteudo = conteudo.replace(old_block, new_block)
    print("✅ Fallback do DMPL injetado com sucesso no PDF.")
else:
    print("⚠️ O bloco exato não foi encontrado. Procurando variações de encoding...")
    # Se falhar por causa dos acentos no "Módulo", tenta substituir apenas o if not m:
    old_simple = '''            m = modulos_por_nome.get(nome_interno)
            if not m:'''
    new_simple = '''            m = modulos_por_nome.get(nome_interno)
            if not m and "DMPL" in nome_interno:
                m = modulos_por_nome.get("DMPL")
                if not m:
                    m = {"nome": "DMPL", "data_geracao": "N/A"}
            if not m:'''
    if old_simple in conteudo:
        conteudo = conteudo.replace(old_simple, new_simple)
        print("✅ Fallback do DMPL injetado (via bloco simplificado).")
    else:
        print("❌ Não foi possível injetar o fallback. Me avise.")

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
