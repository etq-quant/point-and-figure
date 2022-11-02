import math
import plotly.graph_objects as go


def rounding(val):
    if val > 0:
        return math.ceil(val)
    elif val < 0:
        return math.floor(val)
    else:
        return 0


def run_pnf_plotly(tdf, BOX_SIZE, REVERSAL=3, DAY=300):

    tdf = tdf.sort_values("date").reset_index(drop=True).copy()
    company_name = tdf["name"][0]
    sign = 1
    max_h = tdf.at[0, "high"]
    min_l = tdf.at[0, "low"]
    data = [[min_l, max_h]]
    for k, v in tdf.iterrows():
        if k == 0:
            continue
        h = v["high"]
        l = v["low"]
        if sign == 1:
            if h // BOX_SIZE > max_h // BOX_SIZE:
                data[-1] = [data[-1][0], h]
                max_h = h
            elif l // BOX_SIZE < (max_h // BOX_SIZE) - REVERSAL:
                data.append([max_h, l])
                sign = -1
                min_l = l
        elif sign == -1:
            if l // BOX_SIZE < min_l // BOX_SIZE:
                data[-1] = [data[-1][0], l]
                min_l = l
            elif h // BOX_SIZE > (min_l // BOX_SIZE) + REVERSAL:
                data.append([min_l, h])
                sign = 1
                max_h = h

    BOX = BOX_SIZE
    START = tdf["high"][0] // BOX_SIZE * BOX_SIZE
    changes = [rounding((b - a) / BOX_SIZE) for a, b in data]
    if len(changes) <= 1:
        return None
    # one way to force dimensions is to set the figure size:
    fig = go.Figure()

    def sign(val):
        return val / abs(val)

    pointChanges = []
    for chg in changes:
        pointChanges += [sign(chg)] * abs(chg)

    symbol = {-1: "circle", 1: "x"}
    color = {-1: "#FF6347", 1: "#89C35C"}
    fill_color = {-1: "white", 1: "#89C35C"}
    line_width = {-1: 2, 1: 0}
    chgStart = START
    for ichg, chg in enumerate(changes):
        x = [ichg + 1] * abs(chg)
        y = [chgStart + i * BOX * sign(chg) for i in range(abs(chg))]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(
                    color=fill_color[sign(chg)],
                    size=8,
                    line=dict(color=color[sign(chg)], width=line_width[sign(chg)]),
                ),
                marker_symbol=symbol.get(sign(chg)),
            )
        )
        chgStart += BOX * sign(chg) * (abs(chg) - 2)

    fig.update_layout(
        title_text=company_name,
        title_x=0.5,
        width=max(len(changes) * 20, 600),
        height=max((max(changes) - min(changes)) * 20, 600),
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(showline=False, showgrid=False, showticklabels=False,),
        yaxis=dict(
            title="Price",
            tickformat=".2f",
            gridcolor="#D5D8DC",
            showgrid=True,
            zeroline=True,
            showline=False,
            showticklabels=True,
        ),
    )
    return fig
