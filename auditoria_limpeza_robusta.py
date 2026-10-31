import os
import tokenize
import io
def limpar_python(filepath):
    try:
        with open(filepath, 'rb') as f:
            source = f.read()
        # Remove o BOM (se existir) antes de decodificar
        if source.startswith(b'\xef\xbb\xbf'):
            source = source[3:]
        text = source.decode('utf-8')
        lines = text.splitlines()
        # Encontra os limites de todas as strings (para não apagar linhas dentro delas)
        string_spans = []
        try:
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type == tokenize.STRING:
                    string_spans.append((token.start[0], token.end[0]))
        except Exception as e:
            print(f"[AVISO] Erro de tokenize em {filepath}: {e}")
            return 0
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
        if removidas > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines) + '\n')
        return removidas
    except Exception as e:
        print(f"[ERRO] Falha ao processar {filepath}: {e}")
        return 0
def limpar_web(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        new_lines = [l for l in lines if l.strip() != '']
        removidas = len(lines) - len(new_lines)
        if removidas > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        return removidas
    except Exception as e:
        print(f"[ERRO] Falha ao processar {filepath}: {e}")
        return 0
def auditar_projeto():
    total_removidas = 0
    arquivos_processados = 0
    print("=== INICIANDO AUDITORIA E LIMPEZA SEGURA ===")
    for root, dirs, files in os.walk('.'):
        # Ignora pastas de sistema
        dirs[:] = [d for d in dirs if d not in ['pc_venv', '__pycache__', '.git', 'node_modules']]
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith('.py'):
                removidas = limpar_python(filepath)
                if removidas > 0:
                    print(f"[PY] {filepath}: -{removidas} linhas")
                    total_removidas += removidas
                    arquivos_processados += 1
            elif file.endswith(('.html', '.js', '.css')):
                removidas = limpar_web(filepath)
                if removidas > 0:
                    print(f"[WEB] {filepath}: -{removidas} linhas")
                    total_removidas += removidas
                    arquivos_processados += 1
    print("\n=== RESUMO DA AUDITORIA ===")
    print(f"Total de linhas em branco removidas: {total_removidas}")
    print(f"Total de arquivos otimizados: {arquivos_processados}")
    print("Status: LIMPEZA CONCLUÍDA COM SEGURANÇA!")
auditar_projeto()
