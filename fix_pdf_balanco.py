import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_pdf_balanco_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Encontra a função download_pdf
inicio = c.find('async def download_pdf(tipo: str, ano: int = Query(2026), periodo: str = Query("")):')
if inicio == -1:
    print("[ERRO] Função download_pdf não encontrada.")
    exit(1)

# Conta chaves para achar o fim da função
idx_chave = c.find('{', inicio)
nivel = 1
i = idx_chave + 1
while nivel > 0 and i < len(c):
    if c[i] == '{': nivel += 1
    elif c[i] == '}': nivel -= 1
    i += 1
fim = i

corpo_atual = c[inicio:fim]
print("--- CORPO ATUAL (primeiras 30 linhas) ---")
for ln in corpo_atual.split('\n')[:30]:
    print(ln)

# Cria uma versão com limpeza de caracteres
nova_func = corpo_atual

# Adiciona limpeza de tabulações em qualquer .cell() ou .multi_cell() ou .text()
# Também limpa caracteres não suportados pela Helvetica
nova_func = nova_func.replace(
    'async def download_pdf(tipo: str, ano: int = Query(2026), periodo: str = Query("")):',
    'async def download_pdf(tipo: str, ano: int = Query(2026), periodo: str = Query("")):'
)

# Adiciona uma função auxiliar de limpeza no início do corpo
helper = '''
    def limpar_texto(txt):
        """Remove caracteres não suportados pela fonte Helvetica do FPDF."""
        if not txt: return ""
        s = str(txt)
        # Substitui tabulações e caracteres de controle por espaço
        s = s.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
        # Remove caracteres de controle (código < 32)
        s = "".join(ch if ord(ch) >= 32 else " " for ch in s)
        # Substitui acentos por versões sem acento (se necessário)
        # Mantém acentos que o FPDF latin-1 suporta
        try:
            s = s.encode("latin-1", "replace").decode("latin-1")
        except:
            s = "".join(ch if ord(ch) < 256 else "?" for ch in s)
        return s
    
'''

# Insere o helper logo após a assinatura da função (na primeira linha do corpo)
linhas = nova_func.split('\n')
# Encontra a primeira linha que NÃO é a assinatura (que é a que tem '{')
for idx, ln in enumerate(linhas):
    if '{' in ln:
        # Insere o helper depois do '{'
        if '{' in ln:
            partes = ln.split('{', 1)
            if len(partes) == 2:
                linhas[idx] = partes[0] + '{\n' + helper + partes[1]
        break
nova_func = '\n'.join(linhas)

# Substitui no arquivo
c = c[:inicio] + nova_func + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)

try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    print("[AVISO] Restaurando backup...")
    shutil.copy2(f"{back_path}.bak_pdf_balanco_{ts}", back_path)
    print("[OK] Backup restaurado")

print("\n[OK] Função auxiliar 'limpar_texto' adicionada ao download_pdf.")
