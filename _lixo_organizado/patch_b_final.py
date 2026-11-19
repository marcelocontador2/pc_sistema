import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)

# Localiza o for chave na Funcao B (linha ~8874, dentro do try/except com encontrados = [])
alvo_b = -1
for i in range(8700, 9000):
    if 'for chave, tabela in modulos.items():' in linhas[i]:
        # Checa se o bloco anterior tem 'encontrados = []'
        bloco_anterior = "".join(linhas[max(0,i-20):i])
        if 'encontrados = []' in bloco_anterior:
            alvo_b = i
            break

if alvo_b == -1:
    print("[ERRO] Nao encontrei a Funcao B.")
    sys.exit(1)

# Acha o final do bloco: o proximo 'except Exception as e:' e o append
fim_b = alvo_b
for i in range(alvo_b, len(linhas)):
    if 'except Exception as e:' in linhas[i] and i > alvo_b + 5:
        fim_b = i + 2
        break

print(f"[INFO] Funcao B: linhas {alvo_b+1} a {fim_b}")

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
linhas[alvo_b:fim_b] = [novo_b]
print("[OK] Patch 2 (Funcao B) reaplicado.")

arquivo.write_text("".join(linhas), encoding="utf-8")
print("[OK] Arquivo salvo.")
