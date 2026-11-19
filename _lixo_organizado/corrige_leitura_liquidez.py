import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Corrige a leitura dos dados da Liquidez (usar "dados" como fallback)
# Procura o bloco do elif "Índices de Liquidez"
padrao = re.compile(
    r'(elif nome_interno == "\u00cdndices de Liquidez":\s*\n)(.*?)(?=\n\s+elif nome_interno ==|\n\s+else:)',
    re.DOTALL
)

match = padrao.search(texto)
if match:
    bloco_antigo = match.group(0)
    print("[INFO] Bloco da Liquidez encontrado.")
    
    # Novo bloco completo (com leitura correta de 'dados')
    novo_bloco = '''elif nome_interno == "\u00cdndices de Liquidez":
                    # Pega os dados (que estao dentro de 'dados' na API)
                    base = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) and "dados" in mod_dados else mod_dados
                    
                    liq = base.get("liquidez", {})
                    liq_ant = base.get("liquidez_anterior", {})
                    est = base.get("estrutura", {})
                    est_ant = base.get("estrutura_anterior", {})
                    val = base.get("valores", {})
                    val_ant = base.get("valores_anterior", {})
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Indicadores de liquidez e estrutura patrimonial (atual x anterior).</p>")
                    
                    html_parts.append("<h3>\u00cdndices de Liquidez</h3><table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>")
                    for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>")
                    html_parts.append("<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>")
                    for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>")
                    html_parts.append("</tbody></table>")
                '''
    
    texto = texto[:match.start()] + novo_bloco + texto[match.end():]
    print("[OK] Bloco da Liquidez substituido com leitura de 'dados'.")
else:
    print("[ERRO] Bloco da Liquidez nao encontrado.")

# 2. Salva
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
