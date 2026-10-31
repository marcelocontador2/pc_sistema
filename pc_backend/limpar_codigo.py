import os

def limpar_linhas_em_branco(arquivo):
    print(f"Processando {arquivo}...")
    try:
        # Lê o arquivo ignorando o BOM
        with open(arquivo, 'r', encoding='utf-8-sig') as f:
            linhas = f.readlines()

        linhas_limpas = []
        linha_anterior_em_branco = False
        removidas = 0

        for linha in linhas:
            # Verifica se a linha está vazia (só tem espaços ou quebra de linha)
            esta_em_branco = (linha.strip() == '')
            
            if esta_em_branco:
                # Se a anterior também era em branco, ignora esta
                if linha_anterior_em_branco:
                    removidas += 1
                else:
                    linhas_limpas.append('\n')
                    linha_anterior_em_branco = True
            else:
                linhas_limpas.append(linha)
                linha_anterior_em_branco = False

        # Salva o arquivo limpo, SEM BOM (encoding='utf-8' puro)
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.writelines(linhas_limpas)
            
        print(f"[OK] {arquivo}: {removidas} linhas em branco extras removidas!")
    except Exception as e:
        print(f"[ERRO] Falha ao processar {arquivo}: {e}")

# Limpa o main.py
limpar_linhas_em_branco('main.py')

# Opcional: Limpar os outros arquivos Python importantes
# limpar_linhas_em_branco('matriz_integridade.py')
