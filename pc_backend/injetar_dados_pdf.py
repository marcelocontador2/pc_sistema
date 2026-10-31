from pathlib import Path
import ast

arquivo = Path("main.py")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Encontrar a rota do PDF completo (gerar_pdf_completo_custo_pessoal)
inicio_completo = conteudo.find('def gerar_pdf_completo_custo_pessoal(')
if inicio_completo == -1:
    print("ERRO: nao achei a funcao gerar_pdf_completo_custo_pessoal")
    exit(1)

# 2. Encontrar o trecho onde o Playwright abre a pagina
trecho_goto = 'await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}")'
if trecho_goto not in conteudo:
    print("ERRO: nao achei o page.goto do PDF completo")
    exit(1)

# 3. Substituir o page.goto por um bloco que injeta os dados
# (Vamos usar page.evaluate para preencher os campos diretamente)
novo_bloco = '''await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_completo?periodo={periodo}&entidade={entidade}")
                await page.wait_for_timeout(1000)
                
                # INJECAO DIRETA DOS DADOS (para garantir que o PDF nao fique zerado)
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"http://127.0.0.1:9999/api/custo_pessoal/{periodo}?entidade={entidade}")
                    d = resp.json()
                
                # Formatar numeros
                def fmt_br(v):
                    try:
                        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    except:
                        return "0,00"
                
                rcl = d.get("rcl_total", 0)
                custo = d.get("custo_total", 0)
                limite = d.get("limite_atual", rcl * 0.5)
                margem = d.get("margem_disponivel_atual", limite - custo)
                limite_pct = d.get("limite_pct", 0.5)
                
                # Injetar via JavaScript
                await page.evaluate(f"""
                    document.getElementById('pdf-rcl-total').innerText = '{fmt_br(rcl)}';
                    document.getElementById('pdf-custo-total').innerText = '{fmt_br(custo)}';
                    document.getElementById('pdf-resumo-rcl').innerText = '{fmt_br(rcl)}';
                    document.getElementById('pdf-resumo-custo').innerText = '{fmt_br(custo)}';
                    document.getElementById('pdf-resumo-limite').innerText = '{fmt_br(limite)}';
                    document.getElementById('pdf-resumo-margem').innerText = '{fmt_br(margem)}';
                    document.getElementById('pdf-resumo-pct').innerText = '{(custo/rcl*100 if rcl else 0):.2f}%';
                    document.getElementById('pdf-resumo-pct-margem').innerText = '{(margem/rcl*100 if rcl else 0):.2f}%';
                    document.getElementById('pdf-limite').innerText = '{fmt_br(limite)} ({limite_pct*100:.2f}%)';
                    document.getElementById('conc-limite').innerText = 'R$ {fmt_br(limite)}';
                    document.getElementById('conc-custo').innerText = '{(custo/rcl*100 if rcl else 0):.2f}%';
                    document.getElementById('conc-custo-txt').innerText = 'R$ {fmt_br(custo)}';
                """)
                await page.wait_for_timeout(500)'''

# 4. Substituir no main.py (so a primeira ocorrencia, que e do PDF completo)
conteudo = conteudo.replace(trecho_goto, novo_bloco, 1)

# 5. Fazer o mesmo para o PDF resumo
trecho_goto_resumo = 'await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}")'
if trecho_goto_resumo in conteudo:
    novo_bloco_resumo = '''await page.goto(f"http://127.0.0.1:9999/custo_pessoal_pdf_resumo?periodo={periodo}&entidade={entidade}")
                await page.wait_for_timeout(1000)
                
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"http://127.0.0.1:9999/api/custo_pessoal/{periodo}?entidade={entidade}")
                    d = resp.json()
                
                def fmt_br(v):
                    try:
                        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    except:
                        return "0,00"
                
                rcl = d.get("rcl_total", 0)
                custo = d.get("custo_total", 0)
                limite = d.get("limite_atual", rcl * 0.5)
                margem = d.get("margem_disponivel_atual", limite - custo)
                limite_pct = d.get("limite_pct", 0.5)
                
                await page.evaluate(f"""
                    document.getElementById('pdf-rcl').innerText = '{fmt_br(rcl)}';
                    document.getElementById('pdf-custo').innerText = '{fmt_br(custo)}';
                    document.getElementById('pdf-limite').innerText = '{fmt_br(limite)} ({limite_pct*100:.2f}%)';
                    document.getElementById('pdf-margem').innerText = '{fmt_br(margem)}';
                    document.getElementById('pdf-pct-margem').innerText = '{(margem/rcl*100 if rcl else 0):.2f}%';
                """)
                await page.wait_for_timeout(500)'''
    conteudo = conteudo.replace(trecho_goto_resumo, novo_bloco_resumo, 1)
    print("OK: Injecao no PDF resumo adicionada!")
else:
    print("AVISO: nao achei o page.goto do PDF resumo")

arquivo.write_text(conteudo, encoding="utf-8")

try:
    ast.parse(conteudo)
    print("OK: Injecao no PDF completo adicionada!")
    print("Sintaxe OK!")
except SyntaxError as e:
    print(f"ERRO de sintaxe: {e}")
