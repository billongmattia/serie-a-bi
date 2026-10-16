import plotly.express as px

from app import theme


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _style(fig, height: int = 320):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=16,
        legend_title_text="",
    )
    return fig


def area_chart(df, x, y, title, color=theme.BLUE, fmt=".2f"):
    fig = px.line(df, x=x, y=y, title=title, markers=True, text=y)
    fig.update_traces(
        fill="tozeroy",
        line_color=color,
        fillcolor=rgba(color, 0.25),
        textposition="top center",
        texttemplate="%{text:" + fmt + "}",
    )
    fig.update_yaxes(tickformat=fmt)
    return _style(fig)


def hbar_chart(df, x, y, title, color=theme.BLUE, fmt=".2f", height=None):
    height = height or max(320, 26 * len(df) + 90)
    fig = px.bar(df, x=x, y=y, orientation="h", title=title, text=x)
    fig.update_traces(marker_color=color, texttemplate="%{text:" + fmt + "}", textposition="outside")
    fig.update_yaxes(dtick=1, automargin=True)  # tutte le etichette, non una sì e una no
    return _style(fig, height)


def grouped_bar(df, x, ys, title, colors=None):
    colors = colors or [theme.BLUE, theme.RED]
    fig = px.bar(
        df, x=x, y=ys, barmode="group", title=title,
        color_discrete_sequence=colors, text_auto=True,
        labels={"value": "", "variable": ""},
    )
    return _style(fig)
