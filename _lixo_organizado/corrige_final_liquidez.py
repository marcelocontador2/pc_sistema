import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Corrige o nome do trigger
texto = texto.replace('elif nome_interno == "ÃÂndices de Liquidez":', 'elif nome_interno == "Índices de Liquidez":')

# 2. Remove o bloco HTML desalinhado que está dentro de formula_liq
# O bloco vai desde "                # LIQUIDEZ - Le os dados da API" até "</tbody></table>\n"
import re
texto = re.sub(
    r'\n\s*# LIQUIDEZ - Le os dados da API.*?</tbody></table>\n',
    '\n',
    texto,
    flags=re.DOTALL
)
print("[OK] Bloco HTML desalinhado removido.")

# 3. Corrige a leitura de dados: usa "dados" como fallback
antigo_leitura = '''                elif nome_interno == "Índices de Liquidez":
                    liq = mod_dados.get("liquidez", {})
                    est = mod_dados.get("estrutura", {})
                    liq_ant = mod_dados.get("liquidez_anterior", {})
                    est_ant = mod_dados.get("estrutura_anterior", {})
                    val = mod_dados.get("valores", {})
                    val_ant = mod_dados.get("valores_anterior", {})'''

novo_leitura = '''                elif nome_interno == "Índices de Liquidez":
                    base = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) else {}
                    liq = base.get("liquidez", {})
                    est = base.get("estrutura", {})
                    liq_ant = base.get("liquidez_anterior", {})
                    est_ant = base.get("estrutura_anterior", {})
                    val = base.get("valores", {})
                    val_ant = base.get("valores_anterior", {})'''

if antigo_leitura in texto:
    texto = texto.replace(antigo_leitura, novo_leitura)
    print("[OK] Leitura de dados corrigida (usar 'dados' como fallback).")
else:
    print("[AVISO] Nao encontrei o bloco exato da leitura. Vou tentar substituicao por regex...")
    # Fallback: substitui linha a linha
    import re
    texto = re.sub(
        r'(elif nome_interno == "Índices de Liquidez":\s*\n)(\s+)liq = mod_dados\.get\("liquidez", \{\}\)',
        r'\1\2base = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) else {}\n\2liq = base.get("liquidez", {})',
        texto
    )
    texto = re.sub(
        r'(\s+)est = mod_dados\.get\("estrutura", \{\}\)',
        r'\1est = base.get("estrutura", {})',
        texto
    )
    texto = re.sub(
        r'(\s+)liq_ant = mod_dados\.get\("liquidez_anterior", \{\}\)',
        r'\1liq_ant = base.get("liquidez_anterior", {})',
        texto
    )
    texto = re.sub(
        r'(\s+)est_ant = mod_dados\.get\("estrutura_anterior", \{\}\)',
        r'\1est_ant = base.get("estrutura_anterior", {})',
        texto
    )
    texto = re.sub(
        r'(\s+)val = mod_dados\.get\("valores", \{\}\)',
        r'\1val = base.get("valores", {})',
        texto
    )
    texto = re.sub(
        r'(\s+)val_ant = mod_dados\.get\("valores_anterior", \{\}\)',
        r'\1val_ant = base.get("valores_anterior", {})',
        texto
    )
    print("[OK] Leitura corrigida via regex (fallback).")

# 4. Insere o HTML no lugar certo: dentro do elif, após a definicao das funcoes
# Encontra o fim do bloco do elif "Índices de Liquidez" (antes do proximo elif/else)
# O HTML deve ser inserido APÓS as definicoes de funcoes mas ANTES do proximo elif.

# Procura por "elif nome_interno ==" (o proximo)
import re
match_elif = re.search(r'elif nome_interno == "Índices de Liquidez":(.*?)(?=\n\s+elif nome_interno|$)', texto, re.DOTALL)
if match_elif:
    bloco_atual = match_elif.group(1)
    # Verifica se o HTML ja esta la
    if 'html_parts.append("<h3>Índices de Liquidez</h3>' not in bloco_atual:
        # Insere o HTML no final do bloco (apos as definicoes de funcao)
        novo_bloco = bloco_atual.rstrip() + '''

                    html_parts.append("<h3>Índices de Liquidez</h3><table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>")
                    for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>")
                    html_parts.append("<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>")
                    for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>")
                    html_parts.append("</tbody></table>")
'''
        texto = texto[:match_elif.start(1)] + novo_bloco + texto[match_elif.end(1):]
        print("[OK] HTML da Liquidez inserido no final do bloco elif.")
    else:
        print("[INFO] HTML da Liquidez ja existe no bloco elif.")

# 5. Salva
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
