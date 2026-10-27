
import os
import re
import csv
from fastapi import APIRouter, HTTPException

router = APIRouter()

def _get_csv(tipo, periodo):
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    p_limpo = re.sub(r'[^A-Z0-9]', '_', str(periodo).upper()).strip('_')
    nome = f"{tipo}_{p_limpo}.csv"
    caminho = os.path.join(pasta, nome)
    return caminho if os.path.exists(caminho) else None

def _ler_linhas(caminho):
    if not caminho: return []
    
    # 1. Tenta ler do banco de dados primeiro
    try:
        import sqlite3
        import json
        DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
        nome_arquivo = os.path.basename(caminho)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?", (nome_arquivo,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except Exception:
        pass # Se der erro no banco, segue para o arquivo físico

    # 2. Fallback: Lê do arquivo físico (comportamento antigo)
    try:
        with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
            return [ [col.strip().replace(chr(34), '') for col in row] for row in csv.reader(f, delimiter=';') if row ]
    except Exception:
        return []

def _limpar_valor(valor):
    if not valor: return 0.0
    v = str(valor).upper().replace("R$", "").replace(" ", "").strip()
    if not v or v == '-': return 0.0
    mult = -1.0 if v.endswith('C') else 1.0
    v = v.replace("C", "").replace("D", "")
    v = v.replace(chr(10), "").replace(chr(13), "")
    if ',' in v and '.' in v: v = v.replace(".", "").replace(",", ".")
    elif ',' in v: v = v.replace(",", ".")
    try: return float(v) * mult
    except: return 0.0

@router.get("/gerar_matriz/{periodo}")
async def gerar_matriz(periodo: str):
    try:
        pecas_obrigatorias = ["BALANCETE", "BALANCO_PATRIMONIAL", "BALANCO_FINANCEIRO", "BALANCO_ORCAMENTARIO", "DFC", "DVP", "DMPL"]
        pecas_faltando = []
        
        for peca in pecas_obrigatorias:
            if not _get_csv(peca, periodo):
                pecas_faltando.append(peca)
                
        if pecas_faltando:
            return {"erro": "faltando", "pecas": pecas_faltando}

        l_bal = _ler_linhas(_get_csv("BALANCETE", periodo))
        l_bp  = _ler_linhas(_get_csv("BALANCO_PATRIMONIAL", periodo))
        l_bf  = _ler_linhas(_get_csv("BALANCO_FINANCEIRO", periodo))
        l_bo  = _ler_linhas(_get_csv("BALANCO_ORCAMENTARIO", periodo))
        l_dfc = _ler_linhas(_get_csv("DFC", periodo))
        l_dvp = _ler_linhas(_get_csv("DVP", periodo))
        l_dmpl= _ler_linhas(_get_csv("DMPL", periodo))

        matriz = []
        contador_pendencias = [1]

        def add_linha(nome, bal=0, bp=0, bf=0, bo=0, dfc=0, dvp=0, dmpl=0, is_editable=False):
            valores_brutos = [bal, bp, bf, bo, dfc, dvp, dmpl]
            valores = [v for v in valores_brutos if abs(v) > 0.001]
            
            if len(valores) >= 2:
                if all(abs(abs(v) - abs(valores[0])) < 0.05 for v in valores):
                    conf = "OK"
                else:
                    conf = f"({contador_pendencias[0]})"
                    contador_pendencias[0] += 1
            elif len(valores) == 1:
                conf = "N/A"
            else:
                conf = "VAZIO"

            def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if v != 0 else "-"

            matriz.append({
                "item": nome, "balancete": fmt(bal), "bp": fmt(bp), "bf": fmt(bf),
                "bo": fmt(bo), "dfc": fmt(dfc), "dvp": fmt(dvp), "dmpl": fmt(dmpl), "conf": conf, "is_editable": is_editable
            })

        # Balancete: Varre da direita para a esquerda (Saldo)
        def get_bal(termo):
            for p in l_bal:
                if termo in p[0].upper():
                    for val in reversed(p):
                        v_limpo = val.strip().replace(" ", "").replace("\ufeff", "")
                        if v_limpo and any(c.isdigit() for c in v_limpo):
                            return _limpar_valor(v_limpo)
                    return 0.0
            return 0.0

        # Balancete Movimento (coluna específica: 2=Debito, 3=Credito)
        def get_bal_movimento(termo, coluna):
            for p in l_bal:
                if termo in p[0].upper():
                    if len(p) > coluna:
                        return _limpar_valor(p[coluna])
            return 0.0
            
        # BP: Coluna 1 (Ativo) e Coluna 3 (Passivo)
        def get_bp(termo, is_passivo=False):
            for p in l_bp:
                if len(p) >= 4:
                    txt = p[2].upper() if is_passivo else p[0].upper()
                    if termo in txt: 
                        return _limpar_valor(p[3] if is_passivo else p[1])
            return 0.0

        def get_val(linhas, termo, col):
            for p in linhas:
                if len(p) > col and termo in p[0].upper(): return _limpar_valor(p[col])
            return 0.0

        # ==========================================
        # PREENCHENDO TODOS OS ITENS
        # ==========================================
        
        add_linha("ATIVO", get_bal("1 - ATIVO"), get_bp("TOTAL"))
        add_linha("ATIVO CIRCULANTE", get_bal("1.1 - ATIVO CIRCULANTE"), get_bp("ATIVO CIRCULANTE"))
        add_linha("ATIVO NÃO CIRCULANTE", get_bal("1.2 - ATIVO NÃO CIRCULANTE"), get_bp("ATIVO NÃO CIRCULANTE"))
        add_linha("IMOBILIZADO", get_bal("1.2.3 - IMOBILIZADO"), get_bp("IMOBILIZADO"))
        add_linha("INTANGÍVEIS", get_bal("1.2.4 - INTANGÍVEL"), get_bp("INTANGÍVEL"))
        
        add_linha("PASSIVO CIRCULANTE", get_bal("2.1 - PASSIVO CIRCULANTE"), get_bp("PASSIVO CIRCULANTE", True))
        
        # --- VALORES RESTITUÍVEIS AJUSTADOS ---
        # DISPÊNDIOS: coluna 2 (Débito)
        add_linha("VALORES RESTITUÍVEIS - DISPÊNDIOS", get_bal_movimento("2.1.8.8 - VALORES RESTITUÍVEIS", 3), bf=get_val(l_bf, "VINCULADOS", 4))
        # INGRESSOS: coluna 3 (Crédito)
        add_linha("VALORES RESTITUÍVEIS - INGRESSOS", get_bal_movimento("2.1.8.8 - VALORES RESTITUÍVEIS", 4), bf=get_val(l_bf, "VINCULADOS", 1))

        add_linha("PASSIVO NÃO CIRCULANTE", get_bal("2.2 - PASSIVO NAO-CIRCULANTE"), get_bp("PASSIVO NAO-CIRCULANTE", True))

        # --- PATRIMÔNIO LÍQUIDO COM SINAIS CONTÁBEIS ---
        v23 = get_bal("2.3 - PATRIMÔNIO LIQUIDO")
        v4_vpa = get_bal("4 - VARIAÇÃO PATRIMONIAL AUMENTATIVA")
        v3_vpd = get_bal("3 - VARIAÇÃO PATRIMONIAL DIMINUTIVA")
        pl_balancete = v23 + v4_vpa + v3_vpd
        
        pl_bp = get_bp("TOTAL DO PATRIMÔNIO LÍQUIDO", True)
        pl_dmpl = get_val(l_dmpl, "SALDOS FINAIS", 3)
        add_linha("PATRIMÔNIO LÍQUIDO", pl_balancete, pl_bp, dmpl=next((_limpar_valor(p[8]) for p in l_dmpl if "SALDOS FINAIS" in p[0].strip().upper()), 0.0))
        
        # --- VPA E VPD ---
        vpa_dvp = 0.0
        for p in l_dvp:
            if len(p) > 2 and "VARIAÇÃO PATRIMONIAL AUMENTATIVA" in p[0].upper():
                vpa_dvp = _limpar_valor(p[2])
                break
        add_linha("VPA", v4_vpa, dvp=vpa_dvp)
        
        vpd_dvp = 0.0
        for p in l_dvp:
            if len(p) > 6 and "DIMINUTIVA" in p[4].upper():
                vpd_dvp = _limpar_valor(p[6])
                break
        add_linha("VPD", v3_vpd, dvp=vpd_dvp)

        # --- RECEITAS E DESPESAS ---
        rec_bal = get_bal("6.2.1.2.1 - RECEITAS CORRENTE")
        rec_bf = get_val(l_bf, "RECEITAS CORRENTE", 1)
        rec_bo = get_val(l_bo, "RECEITAS CORRENTE", 6)
        rec_dfc = get_val(l_dfc, "RECEITAS CORRENTE", 2)
        add_linha("RECEITA CORRENTE REALIZADA", 
                  get_bal_movimento("6.2.1.2.1 - RECEITAS CORRENTE", 5), 
                  bf=get_val(l_bf, "RECEITAS CORRENTE", 1), 
                  bo=get_val(l_bo, "RECEITAS CORRENTE", 6), 
                  dfc=next((_limpar_valor(p[3]) for p in l_dfc if "RECEITAS CORRENTE" in p[0].upper()), 0.0))
        desp_bo = get_val(l_bo, "CREDITO DISPONIVEL - DESPESA CORRENTE", 4)
        desp_bal = get_bal("6.2.2.1.3.01.01 - CREDITO EMPENHADO A LIQUIDAR - DESPESA CORRENTE") + get_bal("6.2.2.1.3.04.01 - CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE") + get_bal("6.2.2.1.3.03 - CREDITO EMPENHADO LIQUIDADO A PAGAR")
        add_linha("DESPESAS CORRENTE EMPENHADAS", desp_bal, bo=desp_bo)

        cred_bal = get_bal("6.2.2.1.3.04.01 - CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE")
        cred_bf = get_val(l_bf, "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE", 3)
        cred_bo = get_val(l_bo, "CREDITO DISPONIVEL - DESPESA CORRENTE", 6)
        cred_dfc = get_val(l_dfc, "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE", 2)
        add_linha("CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS CORRENTE", 
                  get_bal("6.2.2.1.3.04.01 - CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE"), 
                  bf=next((_limpar_valor(p[4]) for p in l_bf if len(p) > 4 and "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE" in p[3].upper()), 0.0), 
                  bo=get_val(l_bo, "CREDITO DISPONIVEL - DESPESA CORRENTE", 6), 
                  dfc=next((_limpar_valor(p[3]) for p in l_dfc if "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CORRENTE" in p[0].upper()), 0.0))

        # --- RESTOS A PAGAR (RP) ---
        def get_bo_rp(termo, coluna):
            encontrou_bloco = False
            for p in l_bo:
                if len(p) > coluna:
                    if "RESTOS A PAGAR NÃO PROCESSADOS" in p[0].upper() or "DEMONSTRATIVO DE EXECUÇÃO DOS RESTOS" in p[0].upper():
                        encontrou_bloco = True
                    if encontrou_bloco and termo.upper() in p[0].upper():
                        if termo.upper() != "TOTAL" or "TOTAL:" in p[0].upper():
                            return _limpar_valor(p[coluna])
            return 0.0


        def get_bo_total(termo, coluna):
            total = 0.0
            for p in l_bo:
                if len(p) > coluna and termo.upper() in p[0].upper():
                    total += _limpar_valor(p[coluna])
            return total

        add_linha("RP NÃO PROCESSADOS - A LIQUIDAR", 
                  get_bal("6.3.1.1 - RP NÃO PROCESSADOS A LIQUIDAR"), 
                  bo=get_bo_rp("CREDITO DISPONIVEL - DESPESA CORRENTE", 6))
        
        add_linha("RP NÃO PROCESSADOS - DESPESAS CORRENTES - CANCELADOS", 
                  get_bal_movimento("6.3.1.9.1.01 - DESPESA CORRENTE", 5), 
                  bo=get_bo_rp("OUTRAS DESPESAS CORRENTES", 5))
                  
        add_linha("RP NÃO PROCESSADOS - DESPESAS DE CAPITAL - CANCELADOS", 
                  get_bal_movimento("6.3.1.9.1.02 - DESPESA CAPITAL", 5), 
                  bo=get_bo_rp("CREDITO DISPONIVEL - DESPESA CAPITAL", 5))
                  
        add_linha("RP INSCRITOS EM 31 DE DEZEMBRO DO ANO ANTERIOR", 
                  get_bal("5.3.1 - INSCRIÇÃO DE RP NÃO PROCESSADOS"), 
                  bo=get_bo_rp("TOTAL:", 2))

        add_linha("RP NÃO PROCESSADOS PAGOS", 
                  get_bal("6.3.1.4 - RP NÃO PROCESSADOS PAGOS"), 
                  bo=get_bo_rp("CREDITO DISPONIVEL - DESPESA CORRENTE", 4))
                  
        # Duas buscas distintas: Despesa Capital Liquidada (Col F) e RP Capital Pago (Col E)
        # Para isso, buscamos a linha exata dentro dos seus respectivos blocos
        val_liq_capital = 0.0
        val_rp_capital_pago = 0.0
        achou_rp = False
        for p in l_bo:
            if len(p) > 5:
                if "RESTOS A PAGAR NÃO PROCESSADOS" in p[0].upper():
                    achou_rp = True
                if "CREDITO DISPONIVEL - DESPESA CAPITAL" in p[0].upper():
                    if achou_rp:
                        val_rp_capital_pago = _limpar_valor(p[4]) # Coluna E (4)
                    else:
                        val_liq_capital = _limpar_valor(p[5]) # Coluna F (5)
        
        add_linha("INCORPORAÇÃO DE ATIVOS", 
                  0.0, 
                  bo=val_liq_capital + val_rp_capital_pago, 
                  dvp=get_val(l_dvp, "INCORPORAÇÃO DE ATIVOS", 1))
        
        # --- DFC (Demonstrativo de Fluxo de Caixa) ---
        # Busca o valor na Coluna 3 (Exercício Atual) da DFC
        
        val_dfc_caixa = 0.0
        for p in l_dfc:
            if len(p) > 3 and "CAIXA E EQUIVALENTES DE CAIXA FINAL" in p[0].upper():
                val_dfc_caixa = _limpar_valor(p[3])
                break
        add_linha("CAIXA E EQUIVALENTES DE CAIXA", 
                  get_bal_movimento("1.1.1 - CAIXA E EQUIVALENTES DE CAIXA", 5), 
                  bp=get_val(l_bp, "CAIXA E EQUIVALENTES DE CAIXA", 1), 
                  bf=next((_limpar_valor(p[4]) for p in l_bf if "CAIXA" in p[0].strip().upper()), 0.0), 
                  dfc=next((_limpar_valor(p[3]) for p in l_dfc if "CAIXA E EQUIVALENTES DE CAIXA FINAL" in p[0].upper()), 0.0))
        # O Python usa índice 0, então a linha 34 é o índice 34 no array de linhas
        val_desembolsos = 0.0
        val_outros = 0.0
        
        # Busca pelo texto exato na lista l_dfc (que é a lista de linhas do CSV)
        for i, p in enumerate(l_dfc):
            texto = p[0].strip().upper()
            if texto == "DESEMBOLSOS" and i == 34:
                val_desembolsos = abs(_limpar_valor(p[3]))
            elif "OUTROS DESEMBOLSOS DE INVESTIMENTOS" in texto and i == 35:
                val_outros = abs(_limpar_valor(p[3]))

        val_dfc_capital = val_desembolsos - val_outros

        add_linha("CRÉDITO EMPENHADO LIQUIDADO PAGO - DESPESAS DE CAPITAL", 
                  get_bal("6.2.2.1.3.04.02 - CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CAPITAL"), 
                  bf=next((_limpar_valor(p[4]) for p in l_bf if len(p) > 4 and "CREDITO EMPENHADO LIQUIDADO PAGO - DESPESA CAPITAL" in p[3].upper()), 0.0), 
                  bo=get_val(l_bo, "CREDITO DISPONIVEL - DESPESA CAPITAL", 6), 
                  dfc=val_dfc_capital)
                  
        return {"matriz": matriz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
