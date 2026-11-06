import re, os

print("=" * 70)
print("AUDITORIA: COMO O BOTÃO PDF MONTA A URL")
print("=" * 70)

# Procura o HTML que tem a tabela de relatórios
for arquivo in os.listdir(r"pc_frontend"):
    if arquivo.endswith(".html"):
        caminho = os.path.join(r"pc_frontend", arquivo)
        try:
            c = open(caminho, encoding='utf-8-sig').read()
        except:
            try:
                c = open(caminho, encoding='latin-1').read()
            except:
                continue
        
        # Verifica se tem /download/pdf/ no arquivo
        if '/download/pdf/' in c:
            print(f"\n[ENCONTRADO] {arquivo}")
            # Mostra todos os trechos com /download/pdf/
            for m in re.finditer(r'.{0,100}/download/pdf/[^"\'<>\s]+.{0,100}', c):
                print(f"  ...{m.group(0)}...")
            
            # Verifica como o botão é construído
            idx = c.find('download/pdf')
            if idx != -1:
                print(f"\n--- CONTEXTO ---")
                print(c[max(0,idx-300):idx+300])
