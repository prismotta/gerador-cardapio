import io
import matplotlib.pyplot as plt


def gerar_jpg_lista(df):

    if df.empty:
        df = df.copy()
        df.loc[0] = ["Sem dados"] * len(df.columns)

    buffer = io.BytesIO()

    altura = max(2, 0.5 * len(df))

    fig, ax = plt.subplots(figsize=(10, altura))
    ax.axis("off")

    tabela = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center"
    )

    tabela.auto_set_font_size(False)
    tabela.set_fontsize(8)
    tabela.auto_set_column_width(col=list(range(len(df.columns))))

    plt.savefig(buffer, format="jpg", bbox_inches="tight", dpi=300)
    plt.close(fig)

    buffer.seek(0)
    return buffer


def gerar_jpg_cardapio(df):

    if df.empty:
        df = df.copy()
        df.loc[0] = ["Sem dados"] * len(df.columns)

    buffer = io.BytesIO()

    altura = max(3, 0.6 * len(df))

    fig, ax = plt.subplots(figsize=(12, altura))
    ax.axis("off")

    tabela = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center"
    )

    tabela.auto_set_font_size(False)
    tabela.set_fontsize(9)
    tabela.auto_set_column_width(col=list(range(len(df.columns))))

    plt.savefig(buffer, format="jpg", bbox_inches="tight", dpi=300)
    plt.close(fig)

    buffer.seek(0)
    return buffer