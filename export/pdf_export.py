import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch


# Registrar fonte Unicode (caso disponível)
try:
    pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
    FONTE_PADRAO = "DejaVuSans"
except:
    FONTE_PADRAO = "Helvetica"


def _gerar_pdf_tabela(df, titulo):

    if df.empty:
        df = df.copy()
        df.loc[0] = ["Sem dados"] * len(df.columns)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloCustom",
        parent=styles["Heading1"],
        fontName=FONTE_PADRAO
    )

    elements.append(Paragraph(titulo, estilo_titulo))
    elements.append(Spacer(1, 12))

    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), FONTE_PADRAO),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer


def gerar_pdf_lista(df, titulo="Lista de Compras"):
    return _gerar_pdf_tabela(df, titulo)


def gerar_pdf_cardapio(df, titulo="Cardápio da Semana"):
    return _gerar_pdf_tabela(df, titulo)