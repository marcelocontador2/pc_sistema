import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# O bloco comeca na linha 4516 (index 4515)
inicio = 4515

# Verifica seguranca
if "for chave, tabela in modulos.items():" not in linhas[inicio]:
    print("[ERRO] Linha 4516 nao contem o 'for' esperado. Abortando para nao quebrar o arquivo.")
    sys.exit(1)

# Encontra o fim do bloco: procuramos o 'except Exception as e:' logo depois,
# e depois a primeira linha que NAO esta indentada dentro dele.
# O bloco tem 12 espacos de indentacao base.
fim = inicio
for i in range(inicio, len(linhas)):
    if linhas[i].startswith('            except Exception as e:'):
        fim = i
        # O except pode ter 2 ou 3 linhas (com o append)
        j = i + 1
        while j < len(linhas) and (linhas[j].startswith('                ') or not linhas[j].strip()):
            j += 1
        fim = j
        break

print(f"[INFO] Substituindo linhas {inicio+1} a {fim} ({fim-inicio} linhas).")

novo_bloco = '''        for chave, tabela in modulos.items():
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

linhas[inicio:fim] = [novo_bloco]
arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Patch 2 (Funcao B) aplicado na linha 4516.")
print("[OK] Arquivo salvo.")
