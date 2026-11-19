import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# =====================================================================
# 1. PATCH 2 NA FUNCAO A (linha 6360) - a que a API usa
# =====================================================================
alvo_a = -1
for i in range(6000, 7000):
    if 'for chave, tabela in modulos.items():' in linhas[i] and 'encontrados = {}' in "".join(linhas[max(0,i-10):i]):
        alvo_a = i
        break

if alvo_a == -1:
    print("[ERRO] Nao encontrei a Funcao A. Abortando.")
    sys.exit(1)

# O bloco da Funcao A vai de alvo_a ate o proximo "except Exception as e:"
fim_a = alvo_a
for i in range(alvo_a, len(linhas)):
    if 'except Exception as e:' in linhas[i]:
        fim_a = i + 2
        break

print(f"[INFO] Funcao A: linhas {alvo_a+1} a {fim_a}")

novo_a = '''    for chave, tabela in modulos.items():
        try:
            # [FIX] Busca resultado_json (com fallback para dados_json)
            try:
                cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            except Exception:
                cursor.execute(f"SELECT dados_json, data_geracao FROM {tabela} WHERE periodo LIKE %s ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            
            row = cursor.fetchone()
            
            if row:
                try:
                    dados = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                except Exception:
                    dados = {"raw": row[0]}
                encontrados[chave] = {
                    "nome": nomes_amigaveis[chave],
                    "data_geracao": row[1],
                    "dados": dados
                }
            else:
                faltando.append({"chave": chave, "nome": nomes_amigaveis[chave]})
        except Exception as e:
            faltando.append({"chave": chave, "nome": nomes_amigaveis[chave], "erro": str(e)})
'''
linhas[alvo_a:fim_a] = [novo_a]
print("[OK] Patch 2 aplicado na Funcao A (linha 6360).")

# =====================================================================
# 2. PATCH 3 (DFC) - linha 7060 (agora deslocada)
# =====================================================================
alvo_dfc = -1
for i, l in enumerate(linhas):
    if 'if "caixa" in dados_dfc:' in l:
        alvo_dfc = i
        break

if alvo_dfc == -1:
    print("[ERRO] Nao encontrei o DFC. Abortando.")
    sys.exit(1)

inicio_dfc = alvo_dfc - 1
while inicio_dfc > 0 and not linhas[inicio_dfc].strip().startswith('#'):
    inicio_dfc -= 1
fim_dfc = alvo_dfc
while fim_dfc < len(linhas) and '</tbody></table>")' not in linhas[fim_dfc]:
    fim_dfc += 1
fim_dfc += 1

print(f"[INFO] DFC: linhas {inicio_dfc+1} a {fim_dfc}")

novo_dfc = '''                    # [FIX] Apuracao de Caixa
                    grupos_dfc = [
                        ("Operacional", dados_dfc.get("operacional") or {}),
                        ("Investimento", dados_dfc.get("investimento") or {}),
                        ("Financiamento", dados_dfc.get("financiamento") or {}),
                    ]
                    grupos_dfc = [(n, g) for n, g in grupos_dfc if isinstance(g, dict) and g]
                    if grupos_dfc:
                        html_parts.append("<h3>Apuracao de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        for grupo_nome, grupo in grupos_dfc:
                            for k, v in grupo.items():
                                if isinstance(v, dict):
                                    a = v.get("atual", 0)
                                    ant = v.get("anterior", 0)
                                    var = calc_var(a, ant)
                                    rotulo = f"{grupo_nome} - {k.title()}"
                                    html_parts.append(f"<tr><td>{rotulo}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                    if abs(var) > 0.01:
                                        direcao = "positiva" if var > 0 else "negativa"
                                        textos.append(f"<li>{rotulo}: variacao {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                        html_parts.append("</tbody></table>")
'''
linhas[inicio_dfc:fim_dfc] = [novo_dfc]
print("[OK] Patch 3 (DFC) aplicado.")

# =====================================================================
# 3. PATCH 1 - Nomes e Tabelas
# =====================================================================
texto = "".join(linhas)
nome_liq = "\u00cdndices de Liquidez"
texto = texto.replace('"panorama": "historico_panorama",', '"panorama": "historico_panorama_resultados",')
texto = texto.replace('"integridade": "historico_integridade_matriz",', '"integridade": "historico_integridade",')
texto = texto.replace('"dmpl": "historico_analise_dmpl"', '"dmpl": "historico_dmpl"')
linhas = texto.splitlines(keepends=True)
for i, l in enumerate(linhas):
    if "ndices de Liquidez" in l:
        if '"liquidez":' in l:
            linhas[i] = '        "liquidez": "' + nome_liq + '",\n'
        elif 'nome_interno ==' in l:
            pre = l.split('==')[0]
            linhas[i] = pre + '== "' + nome_liq + '":\n'
        elif '("' in l and '11.' in l:
            pre = l.split('("')[0]
            linhas[i] = pre + '("' + nome_liq + '", "11. ' + nome_liq + ' e Estrutura"),\n'
print("[OK] Patch 1 (nomes/tabelas) aplicado.")

arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Arquivo salvo em UTF-8.")
