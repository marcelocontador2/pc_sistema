"""
Serviços de renderização de PDF para o DVP.
"""
from __future__ import annotations
from typing import Any

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None  # type: ignore


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------
def fmt_brl(valor: float | int | None) -> str:
    """Formata valor como moeda brasileira: 1234.5 -> '1.234,50'."""
    if valor is None:
        valor = 0
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        valor = 0.0
    s = f"{valor:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
COR_HEADER_BG = (0, 51, 102)
COR_HEADER_TXT = (255, 255, 255)
COR_TOTAL_BG = (227, 242, 253)
COR_TOTAL_TXT = (0, 51, 102)
COR_ZEBRA = (245, 245, 245)
COR_BRANCO = (255, 255, 255)
COR_BORDA = (200, 200, 200)


# ---------------------------------------------------------------------------
# Itens da tabela
# ---------------------------------------------------------------------------
ITENS_DVP: list[tuple[str, str, bool, bool]] = [
    ("vpa_financeiras", "VPA Financeiras", False, False),
    ("transf_recebidas", "Transferencias Recebidas", False, False),
    ("outras_vpa", "Outras VPA", False, False),
    ("total_vpa", "TOTAL VPA", True, False),
    ("vpd_financeiras", "VPD Financeiras", False, True),
    ("pessoal_encargos", "Pessoal e Encargos", False, True),
    ("servicos", "Servicos", False, True),
    ("total_vpd", "TOTAL VPD", True, True),
]


# ---------------------------------------------------------------------------
# Renderização da tabela
# ---------------------------------------------------------------------------
def desenhar_tabela_dvp(
    pdf: "FPDF",
    dados: dict[str, Any],
    y_inicial: float = 92.0,
    x0: float = 15.0,
    largura: float = 180.0,
    avisar_ausentes: bool = True,
) -> float:
    """
    Desenha a tabela de indicadores DVP no PDF.
    Retorna o y final (após a tabela).
    """
    y = y_inicial

    # Cabeçalho
    pdf.set_fill_color(*COR_HEADER_BG)
    pdf.rect(x0, y, largura, 9, style="F")
    pdf.set_text_color(*COR_HEADER_TXT)
    pdf.set_font("Arial", "B", 9)
    pdf.set_xy(x0 + 3, y + 2.5)
    pdf.cell(90, 4, "Indicador")
    pdf.set_xy(x0 + 95, y + 2.5)
    pdf.cell(40, 4, "Periodo Atual", align="R")
    pdf.set_xy(x0 + 145, y + 2.5)
    pdf.cell(30, 4, "Periodo Anterior", align="R")
    y += 9

    # Linhas
    for i, (chave, nome, negrito, is_vpd) in enumerate(ITENS_DVP):
        bloco = dados.get(chave) or {}
        if avisar_ausentes and not bloco:
            print(f"[WARN] chave ausente nos dados: {chave}")
        val = bloco.get("atual", 0)
        ant = bloco.get("anterior", 0)

        if negrito:
            pdf.set_fill_color(*COR_TOTAL_BG)
        elif i % 2 == 0:
            pdf.set_fill_color(*COR_ZEBRA)
        else:
            pdf.set_fill_color(*COR_BRANCO)

        pdf.rect(x0, y, largura, 8, style="F")
        pdf.set_draw_color(*COR_BORDA)
        pdf.set_line_width(0.1)
        pdf.line(x0, y + 8, x0 + largura, y + 8)

        if negrito:
            pdf.set_font("Arial", "B", 9)
            pdf.set_text_color(*COR_TOTAL_TXT)
        else:
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(0, 0, 0)

        pdf.set_xy(x0 + 3, y + 2)
        pdf.cell(90, 4, nome)
        pdf.set_xy(x0 + 95, y + 2)
        pdf.cell(40, 4, fmt_brl(val), align="R")
        pdf.set_xy(x0 + 145, y + 2)
        pdf.cell(30, 4, fmt_brl(ant), align="R")

        y += 8

    return y + 6