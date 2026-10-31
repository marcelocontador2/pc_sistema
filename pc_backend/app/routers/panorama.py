"""
Rota do Panorama — versão final (31/10/2026).
Calcula Ativo, Passivo, PL, Receitas, Despesas, Superávit Orçamentário,
Superávit Patrimonial (DVP) e Superávit Financeiro (BP).
"""
import json
import os
import sqlite3
from fastapi import APIRouter, HTTPException

try:
    from matriz_integridade import _limpar_valor
except ImportError:
    def _limpar_valor(v):
        if v is None:
            return 0.0
        s = str(v).strip().replace(".", "").replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return 0.0

router = APIRouter(prefix="/api/panorama", tags=["panorama"])

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "pc_storage", "banco_dados.db"
)


def buscar_valor(linhas, termo, coluna):
    termo = termo.upper().strip()
    for linha in linhas:
        if len(linha) > coluna and termo in str(linha[0]).upper():
            try:
                return abs(_limpar_valor(linha[coluna]))
            except Exception:
                return 0.0
    return 0.0


def calcular_bp(linhas_bp):
    ativo_total = 0.0
    passivo_total = 0.0
    pl = 0.0

    for linha in linhas_bp:
        if len(linha) < 4:
            continue
        col0 = str(linha[0]).upper().strip()
        col2 = str(linha[2]).upper().strip()

        try:
            v1 = abs(_limpar_valor(linha[1])) if len(linha) > 1 else 0.0
            v3 = abs(_limpar_valor(linha[3])) if len(linha) > 3 else 0.0
        except Exception:
            continue

        if col0 == "TOTAL" and v1 > ativo_total:
            ativo_total = v1

        if "TOTAL DO PASSIVO" in col2:
            passivo_total = v3

        if "TOTAL DO PATRIM" in col2 and "QUIDO" in col2:
            pl = v3

    if pl == 0.0:
        pl = ativo_total - passivo_total

    return {
        "ativo_total": ativo_total,
        "passivo_total": passivo_total,
        "patrimonio_liquido": pl,
    }


def calcular_bo(linhas_bo):
    receita = 0.0
    despesa = 0.0

    for linha in linhas_bo:
        if len(linha) > 6:
            col0 = str(linha[0]).upper().strip()
            if "SUB-TOTAL DAS RECEITAS" in col0 or "SUB-TOTAL DAS RECEITA" in col0:
                try:
                    receita = abs(_limpar_valor(linha[6]))
                except Exception:
                    pass
                break

    for linha in linhas_bo:
        if len(linha) > 6:
            col0 = str(linha[0]).upper().strip().rstrip(":")
            if col0 == "TOTAL":
                try:
                    v = abs(_limpar_valor(linha[6]))
                    if v > despesa:
                        despesa = v
                except Exception:
                    pass

    return {"receita_realizada": receita, "despesa_empenhada": despesa}


def calcular_dvp(linhas_dvp):
    """Calcula o superavit/deficit patrimonial do DVP.
    O valor esta na linha 49 (RESULTADO PATRIMONIAL) e linhas seguintes."""
    for i, linha in enumerate(linhas_dvp):
        col0 = str(linha[0]).upper().strip() if len(linha) > 0 else ""
        if "RESULTADO PATRIMONIAL" in col0:
            # O valor pode estar na propria linha ou nas seguintes
            # Tenta a propria linha primeiro
            for val in reversed(linha[1:]):
                if val and str(val).strip():
                    try:
                        return abs(_limpar_valor(val))
                    except Exception:
                        pass
            # Se nao achou, busca nas proximas 5 linhas
            for j in range(i + 1, min(i + 6, len(linhas_dvp))):
                for val in linhas_dvp[j]:
                    if val and str(val).strip():
                        try:
                            v = abs(_limpar_valor(val))
                            if v > 0:
                                return v
                        except Exception:
                            pass
    return 0.0

def calcular_superavit_financeiro(linhas_bp):
    """Calcula o superavit financeiro (Ativo Financeiro - Passivo Financeiro)."""
    ativo_fin = 0.0
    passivo_fin = 0.0
    superavit_direto = 0.0

    for linha in linhas_bp:
        if len(linha) < 2:
            continue
        col0 = str(linha[0]).upper().strip()
        col2 = str(linha[2]).upper().strip() if len(linha) > 2 else ""

        # Tenta pegar direto da linha "Superavit Financeiro"
        if "SUPERAVIT FINANCEIRO" in col0 or "SUPERAVIT/DEFICIT FINANCEIRO" in col0:
            for val in reversed(linha[1:]):
                if val and str(val).strip():
                    try:
                        v = abs(_limpar_valor(val))
                        if v > 0:
                            superavit_direto = v
                            break
                    except Exception:
                        pass

        # Calcula Ativo Financeiro - Passivo Financeiro
        if "ATIVO FINANCEIRO" in col0:
            try:
                if len(linha) > 1:
                    ativo_fin = abs(_limpar_valor(linha[1]))
            except Exception:
                pass
        if "PASSIVO FINANCEIRO" in col2:
            try:
                if len(linha) > 3:
                    passivo_fin = abs(_limpar_valor(linha[3]))
            except Exception:
                pass

    # Se achou o valor direto, usa; senao, calcula
    if superavit_direto > 0:
        return superavit_direto
    return ativo_fin - passivo_fin

def buscar_arquivo(periodo, tipo):
    nome = f"{tipo}_{periodo.replace('-', '_')}.csv"
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dados_json FROM arquivos_importados WHERE nome_arquivo = ?",
            (nome,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else []
    finally:
        conn.close()


@router.get("/{periodo}")
async def api_panorama(periodo: str):
    try:
        linhas_bp = buscar_arquivo(periodo, "BALANCO_PATRIMONIAL")
        if not linhas_bp:
            raise HTTPException(status_code=404, detail=f"Balanco Patrimonial nao encontrado para {periodo}")

        bp = calcular_bp(linhas_bp)
        caixa = buscar_valor(linhas_bp, "CAIXA E EQUIVALENTES", 1) or buscar_valor(linhas_bp, "CAIXA", 1)

        linhas_bo = buscar_arquivo(periodo, "BALANCO_ORCAMENTARIO")
        bo = calcular_bo(linhas_bo)
        superavit_orc = bo["receita_realizada"] - bo["despesa_empenhada"]

        linhas_dvp = buscar_arquivo(periodo, "DVP")
        superavit_patrimonial = calcular_dvp(linhas_dvp)

        superavit_financeiro = calcular_superavit_financeiro(linhas_bp)

        print(f"[PANORAMA] ativo={bp['ativo_total']}, passivo={bp['passivo_total']}, pl={bp['patrimonio_liquido']}")
        print(f"[PANORAMA] receita={bo['receita_realizada']}, despesa={bo['despesa_empenhada']}, superavit={superavit_orc}")
        print(f"[PANORAMA] superavit_patrimonial={superavit_patrimonial}, superavit_financeiro={superavit_financeiro}")

        return {
            "ativo_total": bp["ativo_total"],
            "passivo_total": bp["passivo_total"],
            "patrimonio_liquido": bp["patrimonio_liquido"],
            "caixa_bp": caixa,
            "receita_realizada": bo["receita_realizada"],
            "despesa_empenhada": bo["despesa_empenhada"],
            "superavit_orcamentario": superavit_orc,
            "superavit_patrimonial": superavit_patrimonial,
            "superavit_financeiro": superavit_financeiro,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PANORAMA] ERRO: {e}")
        raise HTTPException(status_code=500, detail=str(e))
