import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_buscar_valores_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza a definição da função buscar_valores
inicio = c.find('def buscar_valores(termo):')
if inicio == -1:
    print("[ERRO] def buscar_valores não encontrada.")
    exit(1)

# Encontra o fim da função: próximo "def " no mesmo nível de indentação (4 espaços ou 0)
# A função original termina com 'return "", ""' — vamos usar isso como âncora
fim_ancora = c.find('return "", ""', inicio)
if fim_ancora == -1:
    print("[ERRO] Fim da função (return) não encontrado.")
    exit(1)

# Pega até o fim da linha do return
fim = c.find('\n', fim_ancora) + 1

funcao_antiga = c[inicio:fim]
print("--- FUNÇÃO ATUAL ---")
print(funcao_antiga)
print("--- FIM ---")

# Nova função: usa 'contains' normalizado (não startswith) e tenta colunas 7/8,
# com fallback para varrer colunas procurando o valor numérico
nova_funcao = '''def buscar_valores(termo):
                def normalizar(s):
                    return s.encode('ascii', 'ignore').decode('ascii').upper().strip()
                termo_norm = normalizar(termo)
                for linha in content.splitlines():
                    linha_norm = normalizar(linha)
                    # Usa contains em vez de startswith, para pegar linhas com prefixo
                    if termo_norm in linha_norm:
                        colunas = linha.split(';')
                        # Tenta colunas 7 e 8 (padrão)
                        val1 = colunas[7].strip() if len(colunas) > 7 else ""
                        val2 = colunas[8].strip() if len(colunas) > 8 else ""
                        # Se a coluna 7 estiver vazia, varre as colunas procurando número
                        if not val1:
                            for idx in range(len(colunas) - 1, -1, -1):
                                v = colunas[idx].strip().replace('.', '').replace(',', '.')
                                try:
                                    float(v)
                                    val1 = colunas[idx].strip()
                                    break
                                except ValueError:
                                    continue
                        return val1, val2
                return "", ""
            '''

c = c[:inicio] + nova_funcao + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_buscar_valores_{ts}", back_path)
    print("[OK] Backup restaurado")
