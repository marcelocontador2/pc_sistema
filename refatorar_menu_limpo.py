import re, shutil, datetime, os

# =========================================================
# 1. DESATIVAR O SCRIPT QUE CAUSA O TREMOR
# =========================================================
arq_js_tremor = "pc_frontend/integridade_menu.js"
if os.path.exists(arq_js_tremor):
    # Renomeia o arquivo para que ele não seja mais carregado
    novo_nome = arq_js_tremor + ".desativado"
    if os.path.exists(novo_nome):
        os.remove(novo_nome)
    os.rename(arq_js_tremor, novo_nome)
    print(f"[OK] Script {arq_js_tremor} desativado (não causa mais tremor).")
else:
    print("[INFO] Script integridade_menu.js não encontrado ou já desativado.")

# =========================================================
# 2. LIMPAR E REORGANIZAR O HTML DO MENU
# =========================================================
arq_html = r"pc_frontend/index.html"
backup = f"pc_frontend\\index_backup_limpo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
shutil.copy2(arq_html, backup)
print(f"[OK] Backup: {backup}\n")

with open(arq_html, "r", encoding="utf-8") as f:
    html = f.read()

# Bloco novo e limpo do menu "Análises Contábeis"
# Substitui desde o <li> de "Conferência" até o final do submenu (antes do fechamento da </ul> principal)
# Para isso, localizamos o "Conferência das Demonstrações" e o próximo "Custo de Pessoal" (último item)
idx_ini = html.find('Conferência das Demonstrações')
idx_fim = html.find('Custo de Pessoal', idx_ini)

if idx_ini != -1 and idx_fim != -1:
    # Encontra o início do <li> que contém "Conferência"
    start_li = html.rfind('<li', 0, idx_ini)
    # Encontra o fim do <li> que contém "Custo de Pessoal"
    end_li = html.find('</li>', idx_fim)
    if end_li == -1:
        # Se não achou </li>, pega até o próximo </ul>
        end_li = html.find('</ul>', idx_fim)
    
    if start_li != -1 and end_li != -1:
        bloco_antigo = html[start_li:end_li+5]
        
        # Novo bloco HTML limpo e na ordem correta
        novo_bloco = '''
    <li style="margin-top: 15px;">
        <a style="display:block; padding:10px 0px; text-decoration:none; color:#003366; font-weight:bold; border-bottom: 2px solid #eee;">Análises Contábeis</a>
        <ul style="list-style: none; padding-left: 15px; margin: 0;">
            <li><a href="/conferencia" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Conferência das Demonstrações</a></li>
            <li><a href="/integridade" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Integridade entre Demonstrações</a></li>
            <li><a href="/analise_orcamentaria" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise Orçamentária (BO)</a></li>
            <li><a href="/analise_financeira_bf" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise Financeira (BF)</a></li>
            <li><a href="/analise_bp" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise BP</a></li>
            <li><a href="/analise_dfc" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise DFC</a></li>
            <li><a href="/analise_patrimonial" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise Patrimonial (DVP)</a></li>
            <li><a href="/composicao_receitas_despesas" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Composição Receitas/Despesas</a></li>
            <li><a href="/liquidez" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Índices de Liquidez</a></li>
            <li><a href="/panorama" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Resultados Gerais</a></li>
            <li><a href="/analise_comparativo_receitas" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Comparativo de Receitas</a></li>
            <li><a href="/analise_comparativo_despesas" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Comparativo de Despesas</a></li>
            <li><a href="/analise_centro_custos" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Análise por Centro de Custos</a></li>
            <li><a href="/analise_custo_pessoal" style="display:block; padding:8px 0px; text-decoration:none; color:#555;">Custo de Pessoal</a></li>
        </ul>
    </li>
'''
        html = html.replace(bloco_antigo, novo_bloco, 1)
        print("[OK] HTML do menu limpo e reorganizado com sucesso.")
    else:
        print("[AVISO] Não foi possível determinar o bloco exato do menu.")
else:
    print("[AVISO] Não encontrei os itens 'Conferência' e 'Custo de Pessoal' no HTML.")

# Salvar o arquivo
with open(arq_html, "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== PRÓXIMO PASSO ===")
print("1. Vá no navegador e aperte Ctrl+Shift+R.")
print("2. O menu deve carregar instantaneamente na ordem correta, sem piscar/tremor.")
