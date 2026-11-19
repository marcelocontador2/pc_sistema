import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")

# Lê o arquivo
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# =====================================================================
# PATCH 3 (DFC) -> Altera primeiro (linhas 7060 a 7072 no editor, index 7059 a 7071)
# =====================================================================
# O bloco original começa na linha 7060 ("# Apuração de Caixa") e vai até 7072 ("</tbody></table>")
# Como o Python é 0-indexed, a linha 7060 é o index 7059.
# Vamos verificar se o index 7059 realmente é o "# Apuração de Caixa" para segurança.
if "# Apura" in linhas[7059] and 'if "caixa" in dados_dfc:' in linhas[7060]:
    novo_bloco_dfc = '''                    # [FIX] Apuração de Caixa (o JSON tem 'operacional', 'investimento', 'financiamento', não 'caixa')
                    grupos_dfc = [
                        ("Operacional", dados_dfc.get("operacional") or {}),
                        ("Investimento", dados_dfc.get("investimento") or {}),
                        ("Financiamento", dados_dfc.get("financiamento") or {}),
                    ]
                    grupos_dfc = [(n, g) for n, g in grupos_dfc if isinstance(g, dict) and g]
                    if grupos_dfc:
                        html_parts.append("<h3>Apuração de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
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
                                        textos.append(f"<li>{rotulo}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                        html_parts.append("</tbody></table>")
'''
    # Substitui as linhas 7059 até 7071 (13 linhas) pelo novo bloco
    linhas[7059:7072] = [novo_bloco_dfc]
    print("[OK] Patch 3 (DFC) aplicado com sucesso.")
else:
    print("[AVISO] O bloco do DFC não está exatamente onde esperávamos. Verifique a linha 7060.")
    # Não sai do script, tenta o Patch 2

# =====================================================================
# PATCH 2 (Função B) -> Como adicionamos/removemos linhas acima, o offset mudou.
# =====================================================================
# O bloco original da Função B estava entre as linhas 8866 e 8890 (index 8865 a 8889).
# Como trocamos 13 linhas por 1 bloco de 23 linhas, o arquivo "ganhou" 10 linhas.
# Então o bloco agora começa no index 8875 (8865 + 10).
# Para segurança, vamos procurar a linha exata que tem "for chave, tabela in modulos.items():"
# a partir da linha 8800 (para não pegar outro for parecido).
index_inicio = -1
for i in range(8800, len(linhas)):
    if "for chave, tabela in modulos.items():" in linhas[i]:
        index_inicio = i
        break

if index_inicio != -1:
    # O bloco vai até a linha que tem 'faltando.append({"nome": nomes_amigaveis.get(chave, chave)})'
    # que corresponde ao final do except (linha 8890 do original, que é index_inicio + 24).
    # Vamos procurar o final do bloco com segurança.
    index_fim = index_inicio
    for i in range(index_inicio, len(linhas)):
        if 'faltando.append({"nome": nomes_amigaveis.get(chave, chave)})' in linhas[i]:
            index_fim = i
            break
    
    if index_fim > index_inicio:
        novo_bloco_b = '''        for chave, tabela in modulos.items():
            try:
                # [FIX] Busca o resultado_json e usa LIKE para não falhar por causa de espaços
                try:
                    cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                except Exception:
                    cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                
                row = cursor.fetchone()
                
                if row:
                    item = {
                        "nome": nomes_amigaveis.get(chave, chave),
                        "data_geracao": row[1] if len(row) > 1 else "Disponível",
                        "id": row[0]
                    }
                    # [FIX] Adiciona os dados do relatório na resposta
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
        linhas[index_inicio:index_fim+1] = [novo_bloco_b]
        print(f"[OK] Patch 2 (Função B) aplicado com sucesso a partir da linha {index_inicio+1}.")
    else:
        print("[AVISO] Não foi possível encontrar o final do bloco da Função B.")
else:
    print("[AVISO] Não foi possível encontrar o início do bloco da Função B.")

# Grava o arquivo
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Arquivo main_legado.py salvo em UTF-8.")
