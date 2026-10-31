import io
import tokenize

filepath = 'pc_backend/main.py'

with open(filepath, 'rb') as f:
    source = f.read()

# Remove o BOM
if source.startswith(b'\xef\xbb\xbf'):
    source = source[3:]

# Decodifica e normaliza as quebras de linha do Windows (\r\n para \n)
text = source.decode('utf-8').replace('\r\n', '\n')
lines = text.splitlines()

string_spans = []
try:
    # Agora o tokenize vai funcionar perfeitamente sem o \r
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type == tokenize.STRING:
            string_spans.append((token.start[0], token.end[0]))
except Exception as e:
    print(f"[ERRO] Falha no tokenize: {e}")
    exit()

new_lines = []
removidas = 0
for i, line in enumerate(lines, start=1):
    if line.strip() == '':
        inside_string = False
        for start, end in string_spans:
            if start <= i <= end:
                inside_string = True
                break
        if inside_string:
            new_lines.append(line) # Preserva linhas em branco dentro de strings
        else:
            removidas += 1
    else:
        new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')

print(f"[OK] main.py: {removidas} linhas em branco removidas com sucesso!")
