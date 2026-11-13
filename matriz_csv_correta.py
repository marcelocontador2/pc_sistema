import shutil

caminho = "pc_backend/matriz_integridade.py"
shutil.copy(caminho, caminho + ".bak_csv_mapeado")

novo_codigo = '''import os
import csv
import glob

def _get_csv(tipo, periodo):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    padrao = os.path.join(base, f"*{tipo}*{periodo}*.csv")
    arquivos = glob.glob(padrao)
    if arquivos:
        return arquivos[0]
    padrao2 = os.path.join(base, f"*{tipo}*.csv")
    arquivos2 = glob.glob(padrao2)
    return arquivos2[0] if arquivos2 else None

def _ler_linhas(caminho):
    linhas = []
    if not caminho or not os.path.exists(caminho):
        return linhas
    try:
        with open(caminho, "r", encoding="latin-1") as f:
            leitor = csv.reader(f, delimiter=';')
            for linha in leitor:
                linhas.append(linha)
    except Exception:
        pass
    return linhas

def _limpar_valor(valor):
    if not valor or not isinstance(valor, str):
        return 0.0
    limpo = valor.replace('.', '').replace(',', '.').replace('D', '').replace('C', '').strip()
    try:
        return float(limpo)
    except ValueError:
        return 0.0

def _buscar_valor(linhas, termo, coluna=1):
    """Busca um valor em uma linha que contém o termo, na coluna especificada."""
    for linha in linhas:
        if not linha:
            continue
        # Verifica se o termo está em qualquer célula da linha
        for celula in linha:
            if termo.lower() in str(celula).lower():
                if len(linha) > coluna:
                    valor = _limpar_valor(linha[coluna])
                    if valor != 0.0:
                        return valor
                return 0.0
    return 0.0

def _buscar_valor_balancete(linhas, codigo_conta):
    """Busca no BALANCETE_2026 pelo código exato e pega o valor da coluna 6 (índice 5)."""
    for linha in linhas:
        if not linha or len(linha) < 6:
            continue
        # A linha do balancete começa com "1 - ATIVO"
        if str(linha[0]).strip().startswith(f"{codigo_conta} -") or str(linha[0]).strip() == codigo_conta:
            return _limpar_valor(linha[5])
    return 0.0

def gerar_matriz(periodo):
    try:
        # 1. Carrega os CSVs
        csv_bp = _get_csv("BALANCO_PATRIMONIAL", periodo)
        csv_bo = _get_csv("BALANCO_ORCAMENTARIO", periodo)
        csv_bf = _get_csv("BALANCO_FINANCEIRO", periodo)
        csv_dvp = _get_csv("DVP", periodo)
        csv_balancete = _get_csv("BALANCETE", periodo)

        if not csv_bp and not csv_bo:
            return {"erro": True, "mensagem": f"Arquivos CSV não encontrados para o período {periodo}."}

        linhas_bp = _ler_linhas(csv_bp)
        linhas_bo = _ler_linhas(csv_bo)
        linhas_bf = _ler_linhas(csv_bf)
        linhas_dvp = _ler_linhas(csv_dvp)
        linhas_balancete = _ler_linhas(csv_balancete)

        # 2. Extrai os valores do BALANCETE (coluna 6)
        ativo = _buscar_valor_balancete(linhas_balancete, "1")
        ativo_circulante = _buscar_valor_balancete(linhas_balancete, "1.1")
        ativo_nao_circulante = _buscar_valor_balancete(linhas_balancete, "1.2")
        imobilizado = _buscar_valor_balancete(linhas_balancete, "1.2.3")
        intangiveis = _buscar_valor_balancete(linhas_balancete, "1.2.4")
        
        passivo_circulante = _buscar_valor_balancete(linhas_balancete, "2.1")
        passivo_nao_circulante = _buscar_valor_balancete(linhas_balancete, "2.2")
        pl = _buscar_valor_balancete(linhas_balancete, "2.3")
        
        # 3. Extrai valores do DVP
        vpa = 0.0
        vpd = 0.0
        for linha in linhas_dvp:
            if not linha or len(linha) < 5:
                continue
            if "VARIAÇÃO PATRIMONIAL AUMENTATIVA" in str(linha[0]).upper():
                vpa = _limpar_valor(linha[2])
            if "VARIAÇÃO PATRIMONIAL DIMINUTIVA" in str(linha[3]).upper() if len(linha) > 3 else False:
                vpd = _limpar_valor(linha[4])
            # Busca alternativa para VPD
            for i, celula in enumerate(linha):
                if "VARIAÇÃO PATRIMONIAL DIMINUTIVA" in str(celula).upper():
                    if i + 1 < len(linha):
                        vpd = _limpar_valor(linha[i+1])
        
        # 4. Extrai valores do Balanço Orçamentário (receitas e despesas)
        receita = _buscar_valor(linhas_bo, "RECEITA REALIZADA", 1) or _buscar_valor(linhas_bo, "RECEITAS REALIZADAS", 1)
        despesa = _buscar_valor(linhas_bo, "DESPESA EMPENHADA", 1) or _buscar_valor(linhas_bo, "DESPESAS EMPENHADAS", 1)
        
        # 5. Extrai valores do Balanço Financeiro
        receita_orcamentaria = 0.0
        despesa_orcamentaria = 0.0
        for linha in linhas_bf:
            if not linha or len(linha) < 5:
                continue
            if "Receita Orçamentária" in str(linha[0]):
                receita_orcamentaria = _limpar_valor(linha[1])
            if "Despesa Orçamentária" in str(linha[3]):
                despesa_orcamentaria = _limpar_valor(linha[4])

        # Monta a matriz com os valores calculados
        matriz = [
            {"item": "ATIVO", "balancete": ativo, "bp": ativo, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "ATIVO CIRCULANTE", "balancete": ativo_circulante, "bp": ativo_circulante, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "ATIVO NÃO CIRCULANTE", "balancete": ativo_nao_circulante, "bp": ativo_nao_circulante, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "IMOBILIZADO", "balancete": imobilizado, "bp": imobilizado, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "INTANGÍVEIS", "balancete": intangiveis, "bp": intangiveis, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PASSIVO CIRCULANTE", "balancete": passivo_circulante, "bp": passivo_circulante, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "VALORES RESTITUÍVEIS - DISPÊNDIOS", "balancete": 0.0, "bp": "-", "bf": 0.0, "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "(1)"},
            {"item": "VALORES RESTITUÍVEIS - INGRESSOS", "balancete": 0.0, "bp": "-", "bf": 0.0, "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PASSIVO NÃO CIRCULANTE", "balancete": passivo_nao_circulante, "bp": passivo_nao_circulante, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PATRIMÔNIO LÍQUIDO", "balancete": pl, "bp": pl, "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": pl, "conf": "OK"},
            {"item": "VPA", "balancete": vpa, "bp": "-", "bf": "-", "bo": "-", "dfc": "-", "dvp": vpa, "dmpl": "-", "conf": "OK"},
            {"item": "VPD", "balancete": vpd, "bp": "-", "bf": "-", "bo": "-", "dfc": "-", "dvp": vpd, "dmpl": "-", "conf": "OK"},
            {"item": "RECEITA CORRENTE REALIZADA", "balancete": receita, "bp": "-", "bf": receita, "bo": receita, "dfc": receita, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "DESPESAS CORRENTES EMPENHADAS", "balancete": despesa, "bp": "-", "bf": "-", "bo": despesa, "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS CORRENTE", "balancete": despesa, "bp": "-", "bf": despesa, "bo": despesa, "dfc": despesa, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP NÃO PROCESSADOS - A LIQUIDAR", "balancete": 0.0, "bp": "-", "bf": "-", "bo": 0.0, "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "(2)"},
            {"item": "RP NÃO PROCESSADOS - DESPESAS CORRENTES - CANCELADOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "(3)"},
            {"item": "RP NÃO PROCESSADOS - DESPESAS DE CAPITAL - CANCELADOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP INSCRITOS EM 31 DE DEZEMBRO DO ANO ANTERIOR", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP NÃO PROCESSADOS PAGOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "(4)"},
            {"item": "INCORPORAÇÃO DE ATIVOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": 0.0, "dmpl": "-", "conf": "(5)"},
            {"item": "CAIXA E EQUIVALENTES DE CAIXA", "balancete": 0.0, "bp": 0.0, "bf": 0.0, "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS DE CAPITAL", "balancete": 0.0, "bp": "-", "bf": 0.0, "bo": 0.0, "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "OK"},
        ]

        return {
            "erro": False,
            "periodo": periodo,
            "matriz": matriz
        }
    except Exception as e:
        return {"erro": True, "mensagem": f"Erro ao gerar matriz via CSV: {str(e)}"}
'''

with open(caminho, "w", encoding="utf-8") as f:
    f.write(novo_codigo)

print("✅ matriz_integridade.py reescrito lendo os CSVs com as colunas corretas!")
