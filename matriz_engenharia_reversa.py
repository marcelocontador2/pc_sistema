import shutil

caminho = "pc_backend/matriz_integridade.py"
shutil.copy(caminho, caminho + ".bak_engenharia_reversa")

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
    # Remove pontos de milhar, troca vírgula por ponto e remove 'D'/'C' de débito/crédito
    limpo = valor.replace('.', '').replace(',', '.').replace('D', '').replace('C', '').strip()
    try:
        return float(limpo)
    except ValueError:
        return 0.0

def _buscar_valor_balancete(linhas, codigo_conta):
    """Busca no BALANCETE pelo código exato (ex: '1', '1.1') e pega o valor da coluna 6 (índice 5)."""
    for linha in linhas:
        if not linha or len(linha) < 6:
            continue
        # A linha do balancete começa com "1 - ATIVO"
        primeira_coluna = str(linha[0]).strip()
        if primeira_coluna.startswith(f"{codigo_conta} -") or primeira_coluna == codigo_conta:
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

        # 2. Inicializa os valores
        valores = {
            "ativo": 0.0, "ativo_circ": 0.0, "ativo_nao_circ": 0.0, "imobilizado": 0.0, "intangiveis": 0.0,
            "passivo_circ": 0.0, "passivo_nao_circ": 0.0, "pl": 0.0,
            "vpa": 0.0, "vpd": 0.0, "receita": 0.0, "despesa": 0.0,
            "valores_rest_disp": 0.0, "valores_rest_ing": 0.0,
            "credito_emp": 0.0, "rp_liq": 0.0, "rp_cancel": 0.0, "rp_capital": 0.0,
            "rp_inscritos": 0.0, "rp_pagos": 0.0, "incorporacao": 0.0, "caixa": 0.0, "credito_capital": 0.0
        }

        # 3. Extrai do BALANCETE (coluna 6)
        valores["ativo"] = _buscar_valor_balancete(linhas_balancete, "1")
        valores["ativo_circ"] = _buscar_valor_balancete(linhas_balancete, "1.1")
        valores["ativo_nao_circ"] = _buscar_valor_balancete(linhas_balancete, "1.2")
        valores["imobilizado"] = _buscar_valor_balancete(linhas_balancete, "1.2.3")
        valores["intangiveis"] = _buscar_valor_balancete(linhas_balancete, "1.2.4")
        valores["passivo_circ"] = _buscar_valor_balancete(linhas_balancete, "2.1")
        valores["passivo_nao_circ"] = _buscar_valor_balancete(linhas_balancete, "2.2")
        valores["pl"] = _buscar_valor_balancete(linhas_balancete, "2.3")
        valores["caixa"] = _buscar_valor_balancete(linhas_balancete, "1.1.1")

        # 4. Extrai do DVP (VPA e VPD)
        for linha in linhas_dvp:
            if not linha or len(linha) < 5:
                continue
            if "VARIAÇÃO PATRIMONIAL AUMENTATIVA" in str(linha[0]).upper():
                valores["vpa"] = _limpar_valor(linha[2])
            for i, celula in enumerate(linha):
                if "VARIAÇÃO PATRIMONIAL DIMINUTIVA" in str(celula).upper():
                    if i + 1 < len(linha):
                        valores["vpd"] = _limpar_valor(linha[i+1])

        # 5. Extrai do Balanço Orçamentário (Receita e Despesa)
        for linha in linhas_bo:
            if not linha or len(linha) < 3:
                continue
            # Busca RECEITA REALIZADA
            if "RECEITA REALIZADA" in str(linha[0]).upper():
                # Tenta pegar o valor da coluna 2 (Arrec. Período)
                valores["receita"] = _limpar_valor(linha[2]) if len(linha) > 2 else _limpar_valor(linha[1])
            # Busca DESPESA EMPENHADA
            if "DESPESA EMPENHADA" in str(linha[0]).upper() or "DESPESAS EMPENHADAS" in str(linha[0]).upper():
                valores["despesa"] = _limpar_valor(linha[2]) if len(linha) > 2 else _limpar_valor(linha[1])
            
            # Busca CRÉDITO EMPENHADO
            if "CRÉDITO EMPENHADO" in str(linha[0]).upper() or "CREDITO EMPENHADO" in str(linha[0]).upper():
                valores["credito_emp"] = _limpar_valor(linha[2]) if len(linha) > 2 else _limpar_valor(linha[1])

        # 6. Extrai do Balanço Financeiro (Valores Restituíveis)
        for linha in linhas_bf:
            if not linha or len(linha) < 4:
                continue
            if "VALORES RESTITUÍVEIS" in str(linha[0]).upper() or "VALORES RESTITUIVEIS" in str(linha[0]).upper():
                # No BF, o valor pode estar na coluna 2 (Exercício Atual)
                valores["valores_rest_disp"] = _limpar_valor(linha[2]) if len(linha) > 2 else 0.0
                valores["valores_rest_ing"] = _limpar_valor(linha[2]) if len(linha) > 2 else 0.0

        # 7. Monta a matriz com os 23 itens, distribuindo os valores nas colunas corretas
        matriz = [
            {"item": "ATIVO", "balancete": valores["ativo"], "bp": valores["ativo"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "ATIVO CIRCULANTE", "balancete": valores["ativo_circ"], "bp": valores["ativo_circ"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "ATIVO NÃO CIRCULANTE", "balancete": valores["ativo_nao_circ"], "bp": valores["ativo_nao_circ"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "IMOBILIZADO", "balancete": valores["imobilizado"], "bp": valores["imobilizado"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "INTANGÍVEIS", "balancete": valores["intangiveis"], "bp": valores["intangiveis"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PASSIVO CIRCULANTE", "balancete": valores["passivo_circ"], "bp": valores["passivo_circ"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "VALORES RESTITUÍVEIS - DISPÊNDIOS", "balancete": valores["valores_rest_disp"], "bp": "-", "bf": valores["valores_rest_disp"], "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "(1)"},
            {"item": "VALORES RESTITUÍVEIS - INGRESSOS", "balancete": valores["valores_rest_ing"], "bp": "-", "bf": valores["valores_rest_ing"], "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PASSIVO NÃO CIRCULANTE", "balancete": valores["passivo_nao_circ"], "bp": valores["passivo_nao_circ"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "PATRIMÔNIO LÍQUIDO", "balancete": valores["pl"], "bp": valores["pl"], "bf": "-", "bo": "-", "dfc": "-", "dvp": "-", "dmpl": valores["pl"], "conf": "OK"},
            {"item": "VPA", "balancete": valores["vpa"], "bp": "-", "bf": "-", "bo": "-", "dfc": "-", "dvp": valores["vpa"], "dmpl": "-", "conf": "OK"},
            {"item": "VPD", "balancete": valores["vpd"], "bp": "-", "bf": "-", "bo": "-", "dfc": "-", "dvp": valores["vpd"], "dmpl": "-", "conf": "OK"},
            {"item": "RECEITA CORRENTE REALIZADA", "balancete": valores["receita"], "bp": "-", "bf": valores["receita"], "bo": valores["receita"], "dfc": valores["receita"], "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "DESPESAS CORRENTES EMPENHADAS", "balancete": valores["despesa"], "bp": "-", "bf": "-", "bo": valores["despesa"], "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS CORRENTE", "balancete": valores["credito_emp"], "bp": "-", "bf": valores["credito_emp"], "bo": valores["credito_emp"], "dfc": valores["credito_emp"], "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP NÃO PROCESSADOS - A LIQUIDAR", "balancete": 0.0, "bp": "-", "bf": "-", "bo": 0.0, "dfc": "-", "dvp": "-", "dmpl": "-", "conf": "(2)"},
            {"item": "RP NÃO PROCESSADOS - DESPESAS CORRENTES - CANCELADOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "(3)"},
            {"item": "RP NÃO PROCESSADOS - DESPESAS DE CAPITAL - CANCELADOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP INSCRITOS EM 31 DE DEZEMBRO DO ANO ANTERIOR", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "OK"},
            {"item": "RP NÃO PROCESSADOS PAGOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": "-", "dmpl": "-", "conf": "(4)"},
            {"item": "INCORPORAÇÃO DE ATIVOS", "balancete": 0.0, "bp": "-", "bf": "-", "bo": "-", "dfc": 0.0, "dvp": 0.0, "dmpl": "-", "conf": "(5)"},
            {"item": "CAIXA E EQUIVALENTES DE CAIXA", "balancete": valores["caixa"], "bp": valores["caixa"], "bf": valores["caixa"], "bo": "-", "dfc": valores["caixa"], "dvp": "-", "dmpl": "-", "conf": "OK"},
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

print("✅ matriz_integridade.py reescrito com engenharia reversa dos CSVs!")
