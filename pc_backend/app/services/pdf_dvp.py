"""
Serviços de renderização de PDF para o DVP.
"""
from __future__ import annotations
from typing import Any

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None  # type: ignore


def _sanitizar_pdf(texto: Any) -> str:
    s = str(texto if texto is not None else "")
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    return s.encode("latin-1", errors="replace").decode("latin-1")


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


COR_HEADER_BG = (0, 51, 102)
COR_HEADER_TXT = (255, 255, 255)
COR_TOTAL_BG = (227, 242, 253)
COR_TOTAL_TXT = (0, 51, 102)
COR_ZEBRA = (245, 245, 245)
COR_BRANCO = (255, 255, 255)
COR_BORDA = (200, 200, 200)

ITENS_DVP: list[tuple[str, str, bool, bool]] = [
    ("vpa_financeiras", "VPA Financeiras", False, False),
    ("transf_recebidas", "Transferências Recebidas", False, False),
    ("outras_vpa", "Outras VPA", False, False),
    ("reversao_provisoes", "Reversão de Provisões", False, False),
    ("total_vpa", "TOTAL VPA", True, False),
    ("vpd_financeiras", "VPD Financeiras", False, True),
    ("pessoal_encargos", "Pessoal e Encargos", False, True),
    ("uso_material_consumo", "Uso de Material de Consumo", False, True),
    ("servicos", "Serviços", False, True),
    ("depreciacao", "Depreciação", False, True),
    ("amortizacao", "Amortização", False, True),
    ("transf_concedidas", "Transferências Concedidas", False, True),
    ("outras_vpd", "Outras VPD", False, True),
    ("tributarias", "Tributárias", False, True),
    ("total_vpd", "TOTAL VPD", True, True),
    ("resultado", "RESULTADO PATRIMONIAL", True, False),
]


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

    pdf.set_fill_color(*COR_HEADER_BG)
    pdf.rect(x0, y, largura, 9, style="F")
    pdf.set_text_color(*COR_HEADER_TXT)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(x0 + 2, y + 2.5)
    pdf.cell(92, 4, _sanitizar_pdf("Indicador"))
    pdf.set_xy(x0 + 96, y + 2.5)
    pdf.cell(40, 4, _sanitizar_pdf("Período Atual"), align="R")
    pdf.set_xy(x0 + 138, y + 2.5)
    pdf.cell(40, 4, _sanitizar_pdf("Período Anterior"), align="R")
    y += 9

    for i, (chave, nome, negrito, is_vpd) in enumerate(ITENS_DVP):
        bloco = dados.get(chave) or {}
        if avisar_ausentes and not bloco and chave in ("total_vpa", "total_vpd", "resultado"):
            print(f"[WARN] chave ausente nos dados: {chave}")
        val = bloco.get("atual", 0)
        ant = bloco.get("anterior", 0)

        if negrito:
            pdf.set_fill_color(*COR_TOTAL_BG)
        elif i % 2 == 0:
            pdf.set_fill_color(*COR_ZEBRA)
        else:
            pdf.set_fill_color(*COR_BRANCO)

        pdf.rect(x0, y, largura, 7.5, style="F")
        pdf.set_draw_color(*COR_BORDA)
        pdf.set_line_width(0.1)
        pdf.line(x0, y + 7.5, x0 + largura, y + 7.5)

        if negrito:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*COR_TOTAL_TXT)
        else:
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(0, 0, 0)

        pdf.set_xy(x0 + 2, y + 1.8)
        pdf.cell(92, 4, _sanitizar_pdf(nome))
        pdf.set_xy(x0 + 96, y + 1.8)
        pdf.cell(40, 4, fmt_brl(val), align="R")
        pdf.set_xy(x0 + 138, y + 1.8)
        pdf.cell(40, 4, fmt_brl(ant), align="R")

        y += 7.5

    return y + 6


def desenhar_grafico_dvp_pdf(
    pdf: "FPDF",
    dados: dict[str, Any],
    y_inicial: float,
    x0: float = 15.0,
    largura: float = 180.0,
    altura: float = 56.0,
) -> float:
    """
    Gera e insere no PDF um gráfico de barras corporativo comparando
    Total VPA, Total VPD e Resultado Patrimonial (Período Atual x Anterior).
    Retorna o y final após o bloco do gráfico.
    """
    import io
    import tempfile
    from matplotlib.ticker import FuncFormatter, MaxNLocator

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception:
        return y_inicial

    vpa_at = float((dados.get("total_vpa") or {}).get("atual") or 0.0)
    vpa_an = float((dados.get("total_vpa") or {}).get("anterior") or 0.0)
    vpd_at = float((dados.get("total_vpd") or {}).get("atual") or 0.0)
    vpd_an = float((dados.get("total_vpd") or {}).get("anterior") or 0.0)
    res_at = float((dados.get("resultado") or {}).get("atual") or 0.0)
    res_an = float((dados.get("resultado") or {}).get("anterior") or 0.0)

    y_topo = y_inicial + 3.0
    if y_topo + altura + 10.0 > (pdf.h - 15.0):
        pdf.add_page()
        y_topo = 20.0

    # Moldura corporativa sutil ao redor do bloco do gráfico
    pdf.set_fill_color(250, 251, 253)
    pdf.set_draw_color(218, 226, 236)
    pdf.set_line_width(0.25)
    pdf.rect(x0, y_topo, largura, altura, style="FD")

    # Faixa superior discreta de cabeçalho do bloco
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(x0, y_topo, largura, 7.0, style="F")
    pdf.line(x0, y_topo + 7.0, x0 + largura, y_topo + 7.0)

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(0, 51, 102)
    pdf.set_xy(x0 + 3.0, y_topo + 1.6)
    pdf.cell(110.0, 4.0, _sanitizar_pdf("ANÁLISE GRÁFICA COMPARATIVA — VPA, VPD E RESULTADO PATRIMONIAL"))

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(x0 + largura - 58.0, y_topo + 1.6)
    pdf.cell(55.0, 4.0, _sanitizar_pdf("Valores em R$"), align="R")

    y_img = y_topo + 8.5
    alt_img = max(36.0, altura - 10.0)

    labels = ["Total VPA", "Total VPD", "Resultado Patrimonial"]
    atual_vals = [vpa_at, vpd_at, res_at]
    ant_vals = [vpa_an, vpd_an, res_an]

    fig, ax = plt.subplots(figsize=(8.2, 2.55), dpi=240)
    fig.patch.set_facecolor("#fafbfd")
    ax.set_facecolor("#ffffff")

    x = np.arange(len(labels))
    w = 0.22
    gap = 0.03

    rects1 = ax.bar(
        x - (w / 2 + gap / 2),
        atual_vals,
        width=w,
        label="Período Atual",
        color="#003366",
        edgecolor="#002244",
        linewidth=0.4,
        zorder=3,
    )
    rects2 = ax.bar(
        x + (w / 2 + gap / 2),
        ant_vals,
        width=w,
        label="Período Anterior",
        color="#7b9bc4",
        edgecolor="#6485b0",
        linewidth=0.4,
        zorder=3,
    )

    ax.axhline(0, color="#94a3b8", linewidth=0.9, zorder=2)
    ax.grid(axis="y", linestyle="--", linewidth=0.55, color="#e2e8f0", zorder=0)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_color("#94a3b8")
    ax.spines["bottom"].set_linewidth(0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.2, fontweight="bold", color="#1e293b")
    ax.tick_params(axis="x", pad=4, length=0)
    ax.tick_params(axis="y", labelsize=7.2, colors="#64748b", length=3, color="#cbd5e1")
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    def _fmt_curto(val):
        if abs(val) >= 1_000_000:
            return f"R$ {val / 1_000_000:.1f}M".replace(".", ",")
        if abs(val) >= 1_000:
            return f"R$ {val / 1_000:.0f}k".replace(".", ",")
        return f"R$ {val:.0f}"

    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _pos: _fmt_curto(v)))

    max_abs = max([abs(v) for v in atual_vals + ant_vals] + [1.0])
    ymin, ymax = ax.get_ylim()
    if min(atual_vals + ant_vals) >= 0:
        ax.set_ylim(0, max(ymax, max_abs * 1.22))
    else:
        ax.set_ylim(min(ymin, -max_abs * 0.16), max(ymax, max_abs * 1.22))

    for r in list(rects1) + list(rects2):
        h = r.get_height()
        if abs(h) > 0:
            rot_txt = _fmt_curto(h)
            y_pos = h + (max_abs * 0.03 if h >= 0 else -max_abs * 0.07)
            ax.text(
                r.get_x() + r.get_width() / 2.0,
                y_pos,
                rot_txt,
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=6.6,
                color="#1e293b",
                fontweight="bold",
            )

    ax.legend(
        frameon=True,
        facecolor="#f8fafc",
        edgecolor="#e2e8f0",
        loc="upper right",
        ncol=2,
        fontsize=7.3,
        labelcolor="#1e293b",
    )

    plt.tight_layout(pad=0.55)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=240, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(buf.getvalue())
        tmp_path = tmp.name

    try:
        pdf.image(tmp_path, x=x0 + 1.5, y=y_img, w=largura - 3.0, h=alt_img)
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass

    return y_topo + altura + 4.0
