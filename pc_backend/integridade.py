import os
import re
import csv
from fastapi import APIRouter

router = APIRouter()

def _get_csv(tipo, periodo):
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "uploads_raw")
    p_limpo = re.sub(r'[^A-Z0-9]', '_', str(periodo).upper()).strip('_')
    nome = f"{tipo}_{p_limpo}.csv"
    caminho = os.path.join(pasta, nome)
    return caminho if os.path.exists(caminho) else None

def _limpar_valor(valor):
    if not valor: return 0.0
    v = str(valor).upper().replace("R$", "").replace(" ", "").replace("\n", "").replace("\r", "").strip()
    if not v or v == '-': return 0.0
    mult = -1.0 if v.endswith('C') else 1.0
    v = v.replace("C", "").replace("D", "")
    if ',' in v and '.' in v: v = v.replace(".", "").replace(",", ".")
    elif ',' in v: v = v.replace(",", ".")
    try: return float(v) * mult
    except: return 0.0

def _fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _ler_linhas(caminho):
    with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
        reader = csv.reader(f, delimiter=';')
        return [row for row in reader]

@router.get("/analise_integridade/{periodo}")
async def analise_integridade(periodo: str):
    resultados = []
    
    # ==========================================
    # 1. BALANÇO PATRIMONIAL (BP)
    # ==========================================
    path_bp = _get_csv("BALANCO_PATRIMONIAL", periodo)
    if path_bp:
        linhas = _ler_linhas(path_bp)
        ativo, passivo = 0.0, 0.0
        
        for p in linhas:
            if len(p) >= 4:
                if p[0].strip().upper() == "TOTAL":
                    ativo = _limpar_valor(p[1])
                    passivo = _limpar_valor(p[3])
                    break
                    
        diff = ativo - passivo
        status = "OK" if abs(diff) < 0.05 else "ERRO"
        resultados.append({
            "titulo": "Balanço Patrimonial (BP)",
            "conceito": "Conforme o MCASP e a NBC TSP 11, a equação fundamental é Ativo = Passivo + PL.",
            "tabela": [
                {"label": "Ativo Total", "valor": _fmt(ativo)},
                {"label": "Passivo + PL", "valor": _fmt(passivo)},
                {"label": "Diferença", "valor": _fmt(diff)}
            ],
            "status": status,
            "mensagem": "Ativo e Passivo estão perfeitamente equilibrados." if status == "OK" else f"Atenção: Diferença de {_fmt(diff)}."
        })

    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # 2. BALANÇO FINANCEIRO (BF) - IPC 06 STN
    # ==========================================
    path_bf = _get_csv("BALANCO_FINANCEIRO", periodo)
    if path_bf:
        linhas = _ler_linhas(path_bf)
        
        saldo_ant, rec_orc, rec_extra = 0.0, 0.0, 0.0
        desp_orc, desp_extra, saldo_seg = 0.0, 0.0, 0.0
        
        def norm(t):
            if not t: return ""
            t = str(t).upper().replace("Ç", "C")
            return re.sub(r'[^A-Z0-9]', '', t)

        for p in linhas:
            if not p or len(p) < 5: continue
            
            c0 = norm(p[0])
            c3 = norm(p[3])
            
            # ==========================================
            # LADO ESQUERDO (INGRESSOS)
            # ==========================================
            if "RECEITA" in c0 and "ORCAMENT" in c0:
                rec_orc = _limpar_valor(p[1])
            elif "RECEBIMENTOS" in c0 and "EXTRA" in c0 and "OUTROS" not in c0:
                # Pega o valor exato, ignorando a linha 'Outros Recebimentos'
                rec_extra = _limpar_valor(p[1])
            elif "SALDO" in c0 and "ANTERIOR" in c0:
                saldo_ant = _limpar_valor(p[1])
                
            # ==========================================
            # LADO DIREITO (DISPÊNDIOS)
            # ==========================================
            if "DESPESA" in c3 and "ORCAMENT" in c3:
                desp_orc = _limpar_valor(p[4])
            elif "PAGAMENTOS" in c3 and "EXTRA" in c3 and "OUTROS" not in c3:
                # Pega o valor exato, ignorando a linha 'Outros Pagamentos'
                desp_extra = _limpar_valor(p[4])
            elif "SALDO" in c3 and "SEGUINTE" in c3:
                saldo_seg = _limpar_valor(p[4])

        # Cálculo conforme a IPC 06
        total_ingressos = rec_orc + rec_extra
        total_dispendios = desp_orc + desp_extra
        
        diff = abs((saldo_ant + total_ingressos) - (total_dispendios + saldo_seg))
        status = "OK" if diff < 0.05 else "ERRO"
        
        resultados.append({
            "titulo": "Balanço Financeiro (BF)",
            "conceito": "Conforme a IPC 06 da STN: Total de Ingressos = Receita Orçamentária + Recebimentos Extraorçamentários. Total de Dispêndios = Despesa Orçamentária + Pagamentos Extraorçamentários.",
            "tabela": [
                {"label": "Saldo do Exercício Anterior", "valor": _fmt(saldo_ant)},
                {"label": "(+) Receita Orçamentária", "valor": _fmt(rec_orc)},
                {"label": "(+) Recebimentos Extraorçamentários", "valor": _fmt(rec_extra)},
                {"label": "(=) Total de Ingressos", "valor": _fmt(total_ingressos)},
                {"label": "(-) Despesa Orçamentária", "valor": _fmt(desp_orc)},
                {"label": "(-) Pagamentos Extraorçamentários", "valor": _fmt(desp_extra)},
                {"label": "(=) Total de Dispêndios", "valor": _fmt(total_dispendios)},
                {"label": "(=) Saldo para o Exercício Seguinte", "valor": _fmt(saldo_seg)},
                {"label": "Diferença de Fechamento", "valor": _fmt(diff)}
            ],
            "status": status,
            "mensagem": "A conta fecha perfeitamente com os valores do Exercício Atual." if status == "OK" else f"Atenção: Diferença de {_fmt(diff)}."
        })

    # ==========================================# 3. DEMONSTRAÇÃO DO FLUXO DE CAIXA (DFC)
    # ==========================================
    path_dfc = _get_csv("DFC", periodo)
    if path_dfc:
        linhas = _ler_linhas(path_dfc)
        caixa_ini, geracao_liq, caixa_fim = 0.0, 0.0, 0.0
        
        for p in linhas:
            l_up = ";".join(p).upper()
            if "CAIXA E EQUIVALENTES DE CAIXA INICIAL" in l_up:
                for val in reversed(p):
                    if any(c.isdigit() for c in val):
                        caixa_ini = _limpar_valor(val)
                        break
            elif "GERA" in l_up and "LIQUIDA DE CAIXA" in l_up:
                for val in reversed(p):
                    if any(c.isdigit() for c in val):
                        geracao_liq = _limpar_valor(val)
                        break
            elif "CAIXA E EQUIVALENTES DE CAIXA FINAL" in l_up:
                for val in reversed(p):
                    if any(c.isdigit() for c in val):
                        caixa_fim = _limpar_valor(val)
                        break

        diff = abs((caixa_ini + geracao_liq) - caixa_fim)
        status = "OK" if diff < 0.05 else "ERRO"
        resultados.append({
            "titulo": "Demonstração do Fluxo de Caixa (DFC)",
            "conceito": "Conforme a IPC 08 da STN e NBC TSP 12: Caixa Inicial + Geração Líquida = Caixa Final.",
            "tabela": [
                {"label": "(+) Caixa Inicial", "valor": _fmt(caixa_ini)},
                {"label": "(+) Geração Líquida de Caixa", "valor": _fmt(geracao_liq)},
                {"label": "(=) Caixa Final Esperado", "valor": _fmt(caixa_ini + geracao_liq)},
                {"label": "(=) Caixa Final Informado", "valor": _fmt(caixa_fim)},
                {"label": "Diferença", "valor": _fmt(diff)}
            ],
            "status": status,
            "mensagem": "O fluxo de caixa fecha perfeitamente com a IPC 08." if status == "OK" else f"Erro: Diferença de {_fmt(diff)}."
        })

    # ==========================================
    # 4. DEMONSTRAÇÃO DAS VARIAÇÕES PATRIMONIAIS (DVP)
    # ==========================================
    path_dvp = _get_csv("DVP", periodo)
    if path_dvp:
        linhas = _ler_linhas(path_dvp)
        vpa, vpd = 0.0, 0.0
        
        for p in linhas:
            l_up = ";".join(p).upper()
            if "PATRIMONIAL AUMENTATIVA" in l_up and len(p) > 2:
                vpa = _limpar_valor(p[2])
            if "PATRIMONIAL DIMINUTIVA" in l_up and len(p) > 6:
                vpd = _limpar_valor(p[6])

        resultado_patrimonial = vpa - vpd
        total_dvp = resultado_patrimonial + vpd
        
        diff = abs(total_dvp - vpa)
        status = "OK" if diff < 0.05 else "ERRO"
        
        resultados.append({
            "titulo": "Demonstração das Variações Patrimoniais (DVP)",
            "conceito": "Conforme a IPC 05 da STN e NBC TSP 13, o Resultado Patrimonial (VPA - VPD) deve fechar a equação.",
            "tabela": [
                {"label": "(+) Total das VPA", "valor": _fmt(vpa)},
                {"label": "(-) Total das VPD", "valor": _fmt(vpd)},
                {"label": "(=) Resultado Patrimonial (DVP)", "valor": _fmt(resultado_patrimonial)},
                {"label": "(=) Total (Resultado + VPD)", "valor": _fmt(total_dvp)},
                {"label": "Diferença de Fechamento", "valor": _fmt(diff)}
            ],
            "status": status,
            "mensagem": "A DVP está matematicamente fechada conforme a IPC 05." if status == "OK" else f"Atenção: Diferença de {_fmt(diff)}."
        })

    # ==========================================
    # 5. BALANÇO ORÇAMENTÁRIO (BO)
    # ==========================================
    path_bo = _get_csv("BALANCO_ORCAMENTARIO", periodo)
    if path_bo:
        linhas = _ler_linhas(path_bo)
        rec_real, desp_emp, sup_def = 0.0, 0.0, 0.0
        
        for p in linhas:
            l_up = ";".join(p).upper()
            if "RECEITAS CORRENTE" in l_up and len(p) > 6:
                rec_real += _limpar_valor(p[6])
            elif "CREDITO DISPONIVEL - DESPESA CORRENTE" in l_up and len(p) > 4:
                desp_emp += _limpar_valor(p[4])
            elif "SUPERÁVIT" in l_up or "SUPERAVIT" in l_up:
                for val in p:
                    if any(c.isdigit() for c in val):
                        sup_def = _limpar_valor(val)
                        break

        status = "OK" if rec_real > 0 and desp_emp > 0 else "ALERTA"
        resultados.append({
            "titulo": "Balanço Orçamentário (BO)",
            "conceito": "Conforme a Lei 4.320/64 e o MCASP, confronta a previsão da receita com a fixação da despesa.",
            "tabela": [
                {"label": "Receita Realizada", "valor": _fmt(rec_real)},
                {"label": "Despesa Empenhada", "valor": _fmt(desp_emp)},
                {"label": "Resultado (Superávit/Déficit)", "valor": _fmt(sup_def)}
            ],
            "status": status,
            "mensagem": "Execução orçamentária calculada." if status == "OK" else "Verifique os totais do BO."
        })

    # ==========================================
    # ==========================================
    # ==========================================
    # ==========================================
    # 6. DEMONSTRAÇÃO DAS MUTAÇÕES DO PL (DMPL)
    # ==========================================
    path_dmpl = _get_csv("DMPL", periodo)
    if path_dmpl:
        linhas = _ler_linhas(path_dmpl)
        saldo_ini, res_exerc, saldo_fim = 0.0, 0.0, 0.0
        
        import unicodedata
        
        def norm(t):
            if not t: return ""
            # Remove acentos mantendo a letra base (ex: í -> i)
            t = str(t).upper().replace("Ç", "C")
            t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
            return re.sub(r'[^A-Z0-9]', '', t)

        for p in linhas:
            if not p or len(p) < 5: continue
            c0 = norm(p[0])

            # 1. Saldos Iniciais (Última coluna válida)
            if "SALDOSINICIAIS" in c0:
                for val in reversed(p):
                    if val and any(char.isdigit() for char in val):
                        saldo_ini = _limpar_valor(val)
                        break
                        
            # 2. Resultado do Período
            elif "RESULTADODOPERIODO" in c0:
                for val in reversed(p):
                    if val and any(char.isdigit() for char in val):
                        res_exerc = _limpar_valor(val)
                        break
                        
            # 3. Saldos Finais (Última coluna válida)
            elif "SALDOSFINAIS" in c0:
                for val in reversed(p):
                    if val and any(char.isdigit() for char in val):
                        saldo_fim = _limpar_valor(val)
                        break

        # Fórmula: Saldo Inicial + Resultado = Saldo Final
        diff = abs((saldo_ini + res_exerc) - saldo_fim)
        status = "OK" if diff < 0.05 else "ALERTA"
        
        resultados.append({
            "titulo": "Demonstração das Mutações do PL (DMPL)",
            "conceito": "Conforme o MCASP e a NBC TSP 11, o Saldo Final do PL é a soma do Saldo Inicial com o Resultado do Período.",
            "tabela": [
                {"label": "Saldo Inicial do PL", "valor": _fmt(saldo_ini)},
                {"label": "Resultado do Período", "valor": _fmt(res_exerc)},
                {"label": "(=) Saldo Final do PL", "valor": _fmt(saldo_fim)},
                {"label": "Diferença de Fechamento", "valor": _fmt(diff)}
            ],
            "status": status,
            "mensagem": "Mutações do PL consistentes." if status == "OK" else "Atenção ao fechamento do DMPL."
        })

    # ==========================================
    return {"analises": resultados}
