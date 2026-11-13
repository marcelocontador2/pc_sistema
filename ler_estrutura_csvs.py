import os
import csv
import glob

pasta = os.path.join("pc_storage", "uploads_raw")

if not os.path.exists(pasta):
    print(f"❌ Pasta não encontrada: {pasta}")
else:
    # Lista todos os CSVs na pasta
    arquivos = glob.glob(os.path.join(pasta, "*.csv"))
    print(f"📁 Pasta: {pasta}")
    print(f"📄 Total de CSVs encontrados: {len(arquivos)}\n")
    
    for arq in arquivos:
        nome = os.path.basename(arq)
        tamanho = os.path.getsize(arq) / 1024  # KB
        print(f"📌 ARQUIVO: {nome} ({tamanho:.1f} KB)")
        
        # Lê as primeiras 10 linhas para entender a estrutura
        try:
            with open(arq, "r", encoding="latin-1") as f:
                leitor = csv.reader(f, delimiter=';')
                print(f"   {'LINHA':<6} | CONTEÚDO")
                print(f"   {'-'*6} | {'-'*80}")
                for i, linha in enumerate(leitor):
                    if i >= 10:
                        break
                    # Trunca cada célula para 25 caracteres para não lotar a tela
                    linha_resumida = [str(c)[:25] for c in linha[:6]]
                    print(f"   {i+1:<6} | {' | '.join(linha_resumida)}")
        except Exception as e:
            print(f"   ❌ Erro ao ler: {e}")
        
        print("-" * 80)
