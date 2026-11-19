import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# 1. Remove o bloco HTML que está dentro da função formula_liq (linhas 7459-7474, index 7458-7473)
# Essas linhas vão desde "# LIQUIDEZ - Le os dados..." até "html_parts.append("</tbody></table>")"
inicio_remover = 7458
fim_remover = 7474

# Verifica se realmente são essas linhas
if "LIQUIDEZ - Le os dados" in linhas[inicio_remover] and "</tbody></table>" in linhas[fim_remover-1]:
    # Remove as linhas
    del linhas[inicio_remover:fim_remover]
    print(f"[OK] Bloco HTML removido de dentro da funcao formula_liq (linhas {inicio_remover+1}-{fim_remover}).")
else:
    print("[ERRO] As linhas nao correspondem ao esperado. Abortando.")
    sys.exit(1)

# 2. Encontra o lugar certo para inserir: antes do elif "Panorama de Resultados"
# Agora a linha do elif mudou porque removemos 16 linhas. Vamos procurar novamente.
posicao_inserir = -1
for i, l in enumerate(linhas):
    if 'elif nome_interno == "Panorama de Resultados":' in l:
        posicao_inserir = i
        break

if posicao_inserir == -1:
    print("[ERRO] Nao achei o elif do Panorama de Resultados.")
    sys.exit(1)

# 3. Insere o bloco corrigido ANTES do elif do Panorama
# A indentacao do elif é de 16 espaços, então o código dentro do bloco deve ter 20 espaços.
bloco_correto = '''                
                # LIQUIDEZ - Le os dados da API (que estao dentro de 'dados')
                base_liq = dados_item.get("dados", dados_item) if isinstance(dados_item, dict) else {}
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

'''

linhas[posicao_inserir:posicao_inserir] = [bloco_correto]
print(f"[OK] Bloco da Liquidez inserido antes do elif Panorama (linha {posicao_inserir+1}).")

# 4. Salva
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Arquivo salvo.")
