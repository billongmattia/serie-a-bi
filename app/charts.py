import plotly.express as px

from app import theme


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _style(fig, height: int = 320, legend: bool = False):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme.INK),
        height=height,
        margin=dict(l=10, r=30, t=30, b=10),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""),
        separators=",.",  # formato italiano: virgola decimale, punto per le migliaia
    )
    fig.update_xaxes(showgrid=False, linecolor=theme.LINE, title_text=None, tickangle=0, tickfont_size=10)
    fig.update_yaxes(gridcolor=theme.LINE, zeroline=False, title_text=None)
    return fig


def _padded_range(values, low_pad: float = 0.6, high_pad: float = 0.4):
    """Intervallo dell'asse y centrato sui dati (non su zero), con spazio per le etichette."""
    values = [float(v) for v in values]
    low, high = min(values), max(values)
    span = (high - low) or abs(high) * 0.1 or 1.0
    axis_low = low - span * low_pad
    if low >= 0:
        axis_low = max(axis_low, 0.0)
    return [axis_low, high + span * high_pad]


def area_chart(df, x, y, color=theme.BLUE, fmt=".2f"):
    fig = px.line(df, x=x, y=y, markers=True, text=y)
    fig.update_traces(
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[[0, rgba(color, 0.04)], [1, rgba(color, 0.35)]],
        ),
        line_color=color,
        line_width=2.5,
        marker_size=7,
        textposition="top center",
        texttemplate="%{text:" + fmt + "}",
        cliponaxis=False,
    )
    fig.update_yaxes(tickformat=fmt, range=_padded_range(df[y]))
    return _style(fig)


def hbar_chart(df, x, y, color=theme.BLUE, fmt=".2f", height=None):
    height = height or max(320, 26 * len(df) + 90)
    fig = px.bar(df, x=x, y=y, orientation="h", text=x)
    fig.update_traces(
        marker_color=color,
        texttemplate="%{text:" + fmt + "}",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_yaxes(dtick=1, automargin=True)  # tutte le etichette, non una sì e una no
    fig.update_xaxes(range=[0, float(df[x].max()) * 1.18])  # spazio per l'etichetta a destra
    return _style(fig, height)


def grouped_bar(df, x, ys, colors=None):
    colors = colors or [theme.BLUE, theme.RED]
    fig = px.bar(
        df, x=x, y=ys, barmode="group",
        color_discrete_sequence=colors, text_auto=True,
        labels={"value": "", "variable": ""},
    )
    return _style(fig, legend=True)
