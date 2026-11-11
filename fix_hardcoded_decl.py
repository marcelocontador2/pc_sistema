import re
p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Remove os 5 paragrafos <b>N.</b> ... </p> do html_declaracao
# Padrao: linha comecando com quote + <p ...><b>N.</b>...ate </p>'
padrao = re.compile(
    r'^[ \t]*\'<p[^\']*?<b>[1-5]\.</b>[^\']*?</p>\'[ \t]*\r?\n',
    re.MULTILINE
)
matches = padrao.findall(s)
print(f'Encontrados: {len(matches)} paragrafos hardcoded')

if len(matches) != 5:
    print('ERRO: esperava 5 paragrafos. Abortando para nao quebrar o codigo.')
    raise SystemExit(1)

s2 = padrao.sub('', s)
# Agora precisamos colocar '+ html_itens_declaracao' no lugar certo
# Onde ficava o bloco: entre o <p>Declaramos...</p> e o <div style=margin-top:50px
# Vamos inserir apos a linha do 'Declaramos...' que termina com ', que:</p>'
ancora = re.compile(
    r'(\'<p[^\']*?>Declaramos[^\']*?, que:</p>\'\r?\n)',
    re.MULTILINE
)
if not ancora.search(s2):
    print('ERRO: ancora Declaramos nao encontrada')
    raise SystemExit(1)
s2 = ancora.sub(r'\1        + html_itens_declaracao' + '\n', s2, count=1)

with open(p, 'w', encoding='utf-8') as f:
    f.write(s2)
print('OK: 5 paragrafos removidos e html_itens_declaracao injetado')
