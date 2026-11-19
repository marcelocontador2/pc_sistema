import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# =====================================================================
# PATCH 3 (DFC) - linhas 7060 a 7072 (index 7059 a 7071)
# ALTERAR PRIMEIRO (numero de linha maior) para nao bagunçar o outro
# =====================================================================
assert 'Apura' in linhas[7059] or 'caixa' in linhas[7059].lower(), f"Linha 7060 inesperada: {linhas[7059]!r}"
assert 'if "caixa" in dados_dfc:' in linhas[7060], f"Linha 7061 inesperada: {linhas[7060]!r}"

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
linhas[7059:7072] = [novo_dfc]
print("[OK] Patch 3 (DFC) aplicado nas linhas 7060-7072.")

# =====================================================================
# PATCH 2 (Funcao B) - linhas 4516 a 4541 (index 4515 a 4540)
# O bloco antigo tem exatamente 26 linhas
# =====================================================================
assert 'for chave, tabela in modulos.items():' in linhas[4515], f"Linha 4516 inesperada: {linhas[4515]!r}"

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
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
'''
linhas[4515:4541] = [novo_b]
print("[OK] Patch 2 (Funcao B) aplicado nas linhas 4516-4541.")

texto = "".join(linhas)

# =====================================================================
# PATCH 1 - Nome Liquidez e Tabelas
# =====================================================================
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
