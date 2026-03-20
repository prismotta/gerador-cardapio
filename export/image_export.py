import io
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "DejaVu Sans"


def _gerar_tabela_jpg(df, largura_base, altura_base):

    if df.empty:
        df = df.copy()
        df.loc[0] = ["Sem dados"] * len(df.columns)

    buffer = io.BytesIO()

    altura = max(altura_base, 0.5 * len(df))
    largura = max(largura_base, 1.2 * len(df.columns))

    fig, ax = plt.subplots(figsize=(largura, altura))
    ax.axis("off")

    tabela = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center"
    )

    tabela.auto_set_font_size(False)
    tabela.set_fontsize(9)
    tabela.auto_set_column_width(col=list(range(len(df.columns))))

    for (row, col), cell in tabela.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")

    plt.savefig(buffer, format="jpg", bbox_inches="tight", dpi=300)
    plt.close(fig)

    buffer.seek(0)
    return buffer


def gerar_jpg_lista(df):
    return _gerar_tabela_jpg(df, largura_base=10, altura_base=3)


def gerar_jpg_cardapio(df):
    return _gerar_tabela_jpg(df, largura_base=12, altura_base=4)