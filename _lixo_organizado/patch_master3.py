import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# =====================================================================
# PASSO 1: Correcoes pontuais (tabelas e nome da Liquidez)
# =====================================================================
nome_liq = "\u00cdndices de Liquidez"

texto = texto.replace(
    '"panorama": "historico_panorama",',
    '"panorama": "historico_panorama_resultados",'
)
texto = texto.replace(
    '"integridade": "historico_integridade_matriz",',
    '"integridade": "historico_integridade",'
)
texto = texto.replace(
    '"dmpl": "historico_analise_dmpl"',
    '"dmpl": "historico_dmpl"'
)

# Corrige as 5 linhas do nome de liquidez (independente de acento)
linhas = texto.splitlines(keepends=True)
for i, l in enumerate(linhas):
    if "ndices de Liquidez" in l:
        if '"liquidez":' in l and 'modulos' not in l and 'nomes' not in l:
            linhas[i] = '        "liquidez": "' + nome_liq + '",\n'
        elif 'nome_interno ==' in l:
            pre = l.split('==')[0]
            linhas[i] = pre + '== "' + nome_liq + '":\n'
        elif '("' in l and '11.' in l:
            pre = l.split('("')[0]
            linhas[i] = pre + '("' + nome_liq + '", "11. ' + nome_liq + ' e Estrutura"),\n'
        elif '"liquidez":' in l:
            linhas[i] = '        "liquidez": "' + nome_liq + '",\n'
texto = "".join(linhas)
print("[OK] Nome Liquidez e tabelas corrigidos.")

# =====================================================================
# PASSO 2: PATCH 3 (DFC) - substitui por texto exato
# =====================================================================
alvo_dfc_ini = '# Apura'
alvo_dfc_if = 'if "caixa" in dados_dfc:'

if alvo_dfc_ini in texto and alvo_dfc_if in texto:
    pos_ini = texto.index(alvo_dfc_ini)
    # volta ate o inicio da linha (indentacao)
    pos_ini = texto.rfind('\n', 0, pos_ini) + 1
    # encontra o '</tbody></table>' logo depois
    pos_fim = texto.index('</tbody></table>")', pos_ini) + len('</tbody></table>")')
    bloco_original = texto[pos_ini:pos_fim]

    novo_dfc = '''                    # [FIX] Apuracao de Caixa (JSON tem operacional/investimento/financiamento)
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
                        html_parts.append("</tbody></table>")'''
    texto = texto[:pos_ini] + novo_dfc + texto[pos_fim:]
    print("[OK] Patch 3 (DFC) aplicado.")
else:
    print("[AVISO] Patch 3 (DFC) nao encontrado.")

# =====================================================================
# PASSO 3: PATCH 2 (Funcao B) - substitui por texto exato
# =====================================================================
alvo_b = '''        for chave, tabela in modulos.items():
            try:
                # Verifica se a tabela existe e tem dados para o periodo
                if chave == "analise_financeira_bf":
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                elif chave == "dmpl":
                    # O DMPL pode ter o periodo em formato ligeiramente diferente, tenta LIKE
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                else:
                    cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo = %s LIMIT 1", (periodo,))
                row = cursor.fetchone()
                
                if row:
                    encontrados.append({
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponivel",
                        "id": row[0]
                    })
                else:
                    faltando.append({
                        "nome": nomes_amigaveis.get(chave, chave)
                    })
            except Exception as e:
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})'''

if alvo_b in texto:
    novo_b = '''        for chave, tabela in modulos.items():
            try:
                # [FIX] Busca resultado_json (com fallback para dados_json)
                try:
                    cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                except Exception:
                    try:
                        cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                    except Exception:
                        cursor.execute(f"SELECT id, data_geracao FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                row = cursor.fetchone()
                
                if row:
                    item = {
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponivel",
                        "id": row[0]
                    }
                    if len(row) > 2 and row[2] is not None:
                        try:
                            item["dados"] = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                        except Exception:
                            item["dados"] = row[2]
                    encontrados.append(item)
                else:
                    faltando.append({
                        "nome": nomes_amigaveis.get(chave, chave)
                    })
            except Exception as e:
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})'''
    texto = texto.replace(alvo_b, novo_b, 1)
    print("[OK] Patch 2 (Funcao B) aplicado.")
else:
    print("[AVISO] Patch 2 (Funcao B) nao encontrado - texto exato nao bateu.")

# =====================================================================
# PASSO 4: Salva
# =====================================================================
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
