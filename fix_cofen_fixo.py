import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_cofen_fixo")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza a função e substitui o bloco de busca da entidade
idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
if idx_inicio == -1:
    print("❌ Função não encontrada.")
else:
    # Substitui apenas o trecho que busca a entidade
    trecho_antigo = '''        # 1. Busca dados da entidade
        cursor.execute("SELECT razao_social, cnpj, contador_nome, contador_crc, contador_uf, contador_cpf, logo_path FROM configuracoes_entidade ORDER BY id DESC LIMIT 1")
        ent_row = cursor.fetchone()
        razao_social = ent_row[0] if ent_row else "COFEN/BR"
        cnpj = ent_row[1] if ent_row else ""
        contador_nome = ent_row[2] if ent_row else ""
        contador_crc = ent_row[3] if ent_row else ""
        contador_uf = ent_row[4] if ent_row else ""
        contador_cpf = ent_row[5] if ent_row else ""
        logo_path = ent_row[6] if ent_row else ""'''
    
    trecho_novo = '''        # 1. Busca dados da entidade COFEN (fixo)
        cursor.execute("SELECT logo_path FROM configuracoes_entidade WHERE razao_social ILIKE '%COFEN%' OR razao_social ILIKE '%Conselho Federal%' ORDER BY id DESC LIMIT 1")
        ent_row = cursor.fetchone()
        logo_path = ent_row[0] if ent_row else ""
        
        # Dados fixos do COFEN
        razao_social = "COFEN - Conselho Federal de Enfermagem"
        cnpj = "47.217.146/0001-57"
        contador_nome = "Marcelo Ribeiro Medeiros"
        contador_crc = "066005O8T"
        contador_uf = "DF"
        contador_cpf = "***.212.***.***"'''
    
    if trecho_antigo in conteudo:
        conteudo = conteudo.replace(trecho_antigo, trecho_novo)
        print("✅ Bloco de busca da entidade substituído pelos dados fixos do COFEN.")
    else:
        print("⚠️ Trecho exato não encontrado. Tentando abordagem alternativa...")
        # Tenta encontrar o bloco de forma mais flexível
        import re
        padrao = r'# 1\. Busca dados da entidade.*?logo_path = ent_row\[6\] if ent_row else ""'
        match = re.search(padrao, conteudo, re.DOTALL)
        if match:
            conteudo = conteudo[:match.start()] + trecho_novo + conteudo[match.end():]
            print("✅ Bloco substituído via regex.")
        else:
            print("❌ Não foi possível localizar o bloco de busca da entidade.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
