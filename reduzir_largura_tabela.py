import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_dfc.html"
shutil.copy2(arq, f"{arq}.bak_largura_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Ajusta a classe .main-content para ter a tabela centralizada com 80% de largura
# e adicionar um padding extra nas laterais
antigo_css = """        .main-content { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }"""

novo_css = """        .main-content { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: center; }
        .tabela-wrapper { width: 80%; }"""

if antigo_css in c:
    c = c.replace(antigo_css, novo_css, 1)
    print("[OK] CSS do container principal ajustado para centralizar.")

# 2. Envolve a tabela em uma div com a classe tabela-wrapper
# Procura o inicio e fim da tabela
antigo_tab = """            <table id="tab">"""
novo_tab = """            <div class="tabela-wrapper">
            <table id="tab">"""

antigo_fim_tab = """                </tbody>
            </table>"""
novo_fim_tab = """                </tbody>
            </table>
            </div>"""

if antigo_tab in c and antigo_fim_tab in c:
    c = c.replace(antigo_tab, novo_tab, 1)
    c = c.replace(antigo_fim_tab, novo_fim_tab, 1)
    print("[OK] Tabela envolvida na div 'tabela-wrapper' (80% de largura).")
else:
    print("[AVISO] Nao foi possivel envolver a tabela. Estrutura mudou?")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Arquivo salvo.")
