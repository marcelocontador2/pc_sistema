import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# O bloco da liquidez comeca na linha 7459 (index 7458)
# e vai ate encontrar o proximo "elif nome_interno" ou algo similar
inicio = 7458
fim = inicio

# Procura o final do bloco (o proximo "elif nome_interno ==" ou "elif nome_interno ==")
for i in range(inicio, len(linhas)):
    if 'elif nome_interno ==' in linhas[i] or 'else:' in linhas[i] and 'nome_interno' in linhas[i-1]:
        fim = i
        break

if fim == inicio:
    # Se nao achou, pega 50 linhas depois
    fim = min(inicio + 50, len(linhas))

print(f"[INFO] Substituindo bloco da Liquidez (linhas {inicio+1} a {fim})")

# Novo bloco corrigido
novo_bloco = '''                        # LIQUIDEZ - Le os dados da API (que estao dentro de 'dados')
                        base_liq = dados_item.get("dados", dados_item) if isinstance(dados_item, dict) else {}
                        liq = base_liq.get("liquidez", {})
                        liq_ant = base_liq.get("liquidez_anterior", {})
                        est = base_liq.get("estrutura", {})
                        est_ant = base_liq.get("estrutura_anterior", {})
                        val = base_liq.get("valores", {})
                        val_ant = base_liq.get("valores_anterior", {})
                        
                        html_parts.append("<h3>Índices de Liquidez</h3><table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>")
                        for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>")
                        html_parts.append("<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>")
                        for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>")
                        html_parts.append("</tbody></table>")
'''

linhas[inicio:fim] = [novo_bloco]
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Bloco da Liquidez substituido.")
