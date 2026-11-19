import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Corrige a leitura do DFC (item 6)
# O template antigo procura por "caixa", mas o JSON novo tem "operacional"
texto = texto.replace('dados_dfc["caixa"]', 'dados_dfc.get("operacional", {})')
texto = texto.replace("dados_dfc['caixa']", 'dados_dfc.get("operacional", {})')
texto = texto.replace('if "caixa" in dados_dfc:', 'if "operacional" in dados_dfc or "caixa" in dados_dfc:')

# 2. Corrige a leitura da Liquidez (item 11)
# O template antigo tenta ler 'dados_item', mas o novo JSON tem tudo dentro de 'dados'
# Vamos garantir que ele leia de 'dados' se existir
padrao_liq = re.compile(r'if "liquidez" in dados_item:(.*?)elif', re.DOTALL)
match_liq = padrao_liq.search(texto)
if match_liq:
    bloco_novo = '''if "liquidez" in dados_item or ("dados" in dados_item and "liquidez" in dados_item["dados"]):
                        # Se os dados estiverem aninhados em 'dados', usa eles
                        base_liq = dados_item.get("dados", dados_item)
                        liq = base_liq.get("liquidez", {})
                        liq_ant = base_liq.get("liquidez_anterior", {})
                        est = base_liq.get("estrutura", {})
                        est_ant = base_liq.get("estrutura_anterior", {})
                        
                        html_parts.append("<h3>Índices de Liquidez</h3><table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>")
                        for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>")
                        html_parts.append("<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>")
                        for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>")
                        html_parts.append("</tbody></table>")
                    elif'''
    texto = padrao_liq.sub(bloco_novo, texto, count=1)
    print("[OK] Bloco da Liquidez corrigido.")
else:
    print("[AVISO] Bloco da Liquidez nao encontrado com o padrao 'if liquidez in dados_item'.")

# 3. Salva
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
