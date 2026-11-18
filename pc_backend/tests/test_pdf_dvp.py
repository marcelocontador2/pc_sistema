"""
Testes de renderização da tabela DVP no PDF.
"""
import pytest
from fpdf import FPDF
from pc_backend.app.services.pdf_dvp import (
    fmt_brl,
    ITENS_DVP,
    desenhar_tabela_dvp,
    COR_HEADER_BG,
    COR_TOTAL_BG,
)


# ---------------------------------------------------------------------------
# fmt_brl
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entrada,esperado", [
    (0, "0,00"),
    (None, "0,00"),
    (1, "1,00"),
    (1234.5, "1.234,50"),
    (1234567.89, "1.234.567,89"),
    (-50, "-50,00"),
    (-1234.5, "-1.234,50"),
    ("100", "100,00"),
    ("abc", "0,00"),
])
def test_fmt_brl(entrada, esperado):
    assert fmt_brl(entrada) == esperado


# ---------------------------------------------------------------------------
# ITENS_DVP
# ---------------------------------------------------------------------------
def test_itens_dvp_tem_8_linhas():
    assert len(ITENS_DVP) == 8


def test_itens_dvp_estrutura():
    for item in ITENS_DVP:
        assert len(item) == 4
        chave, nome, negrito, is_vpd = item
        assert isinstance(chave, str) and chave
        assert isinstance(nome, str) and nome
        assert isinstance(negrito, bool)
        assert isinstance(is_vpd, bool)


def test_itens_dvp_tem_2_totais():
    totais = [it for it in ITENS_DVP if it[2]]
    assert len(totais) == 2
    assert totais[0][0] == "total_vpa"
    assert totais[1][0] == "total_vpd"


def test_itens_dvp_chaves_unicas():
    chaves = [it[0] for it in ITENS_DVP]
    assert len(chaves) == len(set(chaves))


# ---------------------------------------------------------------------------
# desenhar_tabela_dvp
# ---------------------------------------------------------------------------
def _dados_fake():
    return {
        "vpa_financeiras": {"atual": 1000, "anterior": 900},
        "transf_recebidas": {"atual": 500, "anterior": 400},
        "outras_vpa": {"atual": 100, "anterior": 100},
        "total_vpa": {"atual": 1600, "anterior": 1400},
        "vpd_financeiras": {"atual": 800, "anterior": 700},
        "pessoal_encargos": {"atual": 600, "anterior": 550},
        "servicos": {"atual": 300, "anterior": 250},
        "total_vpd": {"atual": 1700, "anterior": 1500},
    }


def test_gera_pdf_com_tabela():
    pdf = FPDF()
    pdf.add_page()
    y_final = desenhar_tabela_dvp(pdf, _dados_fake())
    assert y_final > 92
    out = bytes(pdf.output())
    assert out[:4] == b"%PDF"
    assert len(out) > 1000


def test_gera_pdf_com_dados_faltando_nao_quebra():
    pdf = FPDF()
    pdf.add_page()
    desenhar_tabela_dvp(pdf, {"total_vpa": {"atual": 1, "anterior": 0}})
    out = bytes(pdf.output())
    assert out[:4] == b"%PDF"


def test_gera_pdf_com_dados_vazios_nao_quebra():
    pdf = FPDF()
    pdf.add_page()
    desenhar_tabela_dvp(pdf, {})
    out = bytes(pdf.output())
    assert out[:4] == b"%PDF"


def test_y_inicial_customizado():
    pdf = FPDF()
    pdf.add_page()
    y_final_92 = desenhar_tabela_dvp(pdf, _dados_fake(), y_inicial=92)

    pdf2 = FPDF()
    pdf2.add_page()
    y_final_150 = desenhar_tabela_dvp(pdf2, _dados_fake(), y_inicial=150)

    # Diferenca deve ser exatamente 150 - 92 = 58
    assert abs((y_final_150 - y_final_92) - 58) < 0.01


# ---------------------------------------------------------------------------
# Cores (contrato basico)
# ---------------------------------------------------------------------------
def test_cores_definidas():
    assert COR_HEADER_BG == (0, 51, 102)
    assert COR_TOTAL_BG == (227, 242, 253)