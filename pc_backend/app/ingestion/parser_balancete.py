import pandas as pd
import os
def limpar_valor_contabil(valor_str):
    if pd.isna(valor_str) or str(valor_str).strip() == '':
        return 0.0, None
    valor_str = str(valor_str).strip().upper()
    natureza = None
    if valor_str.endswith('D'):
        natureza = 'D'
        valor_str = valor_str[:-1]
    elif valor_str.endswith('C'):
        natureza = 'C'
        valor_str = valor_str[:-1]
    valor_str = valor_str.replace('R$', '').replace('.', '').replace(',', '.')
    try:
        valor_float = float(valor_str)
    except ValueError:
        valor_float = 0.0
    return valor_float, natureza
def processar_balancete(caminho_csv):
    print(f"Iniciando processamento do arquivo: {caminho_csv}")
    try:
        df = pd.read_csv(caminho_csv, sep=';', skiprows=6, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, sep=';', skiprows=6, encoding='latin-1')
    df.columns = ['codigo_conta', 'descricao_conta', 'saldo_anterior', 'debito', 'credito', 'saldo_atual']
    df = df[df['codigo_conta'].notna()]
    df['saldo_anterior_limpo'] = df['saldo_anterior'].apply(lambda x: limpar_valor_contabil(x)[0])
    df['debito_limpo'] = df['debito'].apply(lambda x: limpar_valor_contabil(x)[0])
    df['credito_limpo'] = df['credito'].apply(lambda x: limpar_valor_contabil(x)[0])
    saldo_atual_info = df['saldo_atual'].apply(limpar_valor_contabil)
    df['saldo_atual_limpo'] = [info[0] for info in saldo_atual_info]
    df['natureza_saldo'] = [info[1] for info in saldo_atual_info]
    df_final = df[['codigo_conta', 'descricao_conta', 'saldo_anterior_limpo', 'debito_limpo', 'credito_limpo', 'saldo_atual_limpo', 'natureza_saldo']].copy()
    df_final.columns = ['codigo_conta', 'descricao_conta', 'saldo_anterior', 'debito', 'credito', 'saldo_atual', 'natureza_saldo']
    print(f"Processamento concluído. {len(df_final)} linhas prontas.")
    return df_final
if __name__ == "__main__":
    # Descobre o caminho absoluto da raiz do projeto
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, "..", "..", ".."))
    arquivo_teste = os.path.join(raiz_projeto, "pc_storage", "uploads_raw", "Balancete.csv")
    if os.path.exists(arquivo_teste):
        df = processar_balancete(arquivo_teste)
        print("\n--- Prévia dos dados limpos ---")
        print(df.head(10))
    else:
        print(f"Arquivo não encontrado: {arquivo_teste}")
        print("Coloque o arquivo Balancete.csv na pasta pc_storage/uploads_raw/")
