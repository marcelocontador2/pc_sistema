import re

c = open('main.py', encoding='utf-8-sig').read()

# Padrão para encontrar o bloco de processamento do CSV dentro da rota upload
padrao = r'if tipo_relatorio and tipo_relatorio\.upper\(\) == "CENTRO_CUSTOS":.*?mensagem = f"Erro ao processar CSV: \{str\(e\)\}"'

# Novo bloco de processamento adaptado ao formato do relatório COFEN
novo_bloco = '''if tipo_relatorio and tipo_relatorio.upper() == "CENTRO_CUSTOS":
        try:
            # Lê o arquivo inteiro
            try:
                with open(caminho, "r", encoding="utf-8-sig") as f:
                    linhas = f.readlines()
            except UnicodeDecodeError:
                with open(caminho, "r", encoding="latin-1") as f:
                    linhas = f.readlines()
            
            centros = []
            # Encontra a linha de cabeçalho (que começa com "Centro de Custo x Conta")
            inicio_dados = 0
            for i, linha in enumerate(linhas):
                if "Centro de Custo x Conta" in linha:
                    inicio_dados = i + 1
                    break
            
            # Pula a linha do "COFEN/BR" se existir (que fica logo após o cabeçalho)
            if inicio_dados < len(linhas) and "COFEN/BR" in linhas[inicio_dados]:
                inicio_dados += 1
                
            # Processa as linhas de dados
            for linha in linhas[inicio_dados:]:
                # Divide por vírgula (ou ponto e vírgula, se for o caso)
                if ";" in linha:
                    partes = linha.strip().split(";")
                else:
                    partes = linha.strip().split(",")
                
                # Se tiver menos de 2 colunas, ignora
                if len(partes) < 2:
                    continue
                
                nome = partes[0].strip().strip('"')
                # Ignora linhas de total ou vazias
                if not nome or "TOTAL" in nome.upper() or nome.startswith("Página"):
                    continue
                
                # O valor "Realizado" geralmente está na última coluna preenchida (ou na coluna 10, índice 10)
                # Vamos pegar o último valor numérico válido da linha
                valor = 0.0
                for parte in reversed(partes):
                    parte_limpa = parte.strip().strip('"').replace(".", "").replace(",", ".")
                    try:
                        valor = float(parte_limpa)
                        if valor > 0:
                            break
                    except:
                        continue
                
                centros.append({"nome": nome, "valor": valor})
            
            if centros:
                # Salva no banco de dados
                import sqlite3, json
                from datetime import datetime
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS historico_centro_custos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
                periodo = f"{ano}-{periodo_tipo}-{periodo_valor}" if ano and periodo_tipo and periodo_valor else "2026-TRIMESTRE-3"
                data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cur.execute("INSERT INTO historico_centro_custos (periodo, data_geracao, dados_json) VALUES (?, ?, ?)",
                           (periodo, data_geracao, json.dumps({"centros": centros})))
                conn.commit()
                conn.close()
                dados_processados = centros
                mensagem = f"Centro de Custos importado com sucesso! ({len(centros)} centros) - Arquivo: {nome_arquivo}"
            else:
                mensagem = "CSV processado, mas nenhum centro encontrado. Verifique o formato."
        except Exception as e:
            mensagem = f"Erro ao processar CSV: {str(e)}"'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Lógica de processamento adaptada ao formato do relatório COFEN!")
else:
    print("[ERRO] Não foi possível encontrar o bloco de processamento. Verifique o código.")

open('main.py', 'w', encoding='utf-8').write(c)
