import math
import numpy as np
import plotly.graph_objects as go


def rounding(val):
    if val > 0:
        return math.ceil(val)
    elif val < 0:
        return math.floor(val)
    else:
        return 0


def round_up(val, box):
    return round(math.ceil(val / box) * box, 4)


def round_down(val, box):
    return round(math.floor(val / box) * box, 4)


def get_sign(val):
    return val / abs(val)


def run_pnf_plotly(tdf, BOX_SIZE, REVERSAL=3, DAY=300):
    tdf = tdf.sort_values("date").reset_index(drop=True).copy()
    company_name = tdf["name"][0]
    sign = 1
    max_h = tdf.at[0, "high"]
    min_l = tdf.at[0, "low"]
    data = [[min_l, min_l, 1]]
    for k, v in tdf.iterrows():
        if k == 0:
            continue
        h = v["high"]
        l = v["low"]
        ph = tdf.loc[k - 1, "high"]
        pl = tdf.loc[k - 1, "low"]
        if sign == 1:
            if h // BOX_SIZE > ph // BOX_SIZE:
                data[-1] = [data[-1][0], h, sign]
                max_h = h
            elif l // BOX_SIZE < (max_h // BOX_SIZE) - REVERSAL:
                data.append([l, max_h - BOX_SIZE, -1])
                sign = -1
                min_l = l
        elif sign == -1:
            if l // BOX_SIZE < pl // BOX_SIZE:
                data[-1] = [data[-1][0], l, sign]
                min_l = l
            elif h // BOX_SIZE > (min_l // BOX_SIZE) + REVERSAL:
                data.append([min_l + BOX_SIZE, h, 1])
                sign = 1
                max_h = h
    BOX = BOX_SIZE

    changes = [
        c
        if a == b
        else round(round_up(b, BOX_SIZE) - round_down(a, BOX_SIZE), 4) / BOX_SIZE + c
        if c == 1
        else round(round_down(b, BOX_SIZE) - round_up(a, BOX_SIZE), 4) / BOX_SIZE + c
        for a, b, c in data
    ]
    changes = [get_sign(c) * math.ceil(abs(c)) for c in changes]
    changes = [int(c) for c in changes]
    # return data, changes
    if len(changes) <= 1:
        return None
    # one way to force dimensions is to set the figure size:
    fig = go.Figure()
    symbol = {-1: "circle", 1: "x"}
    color = {-1: "#FF6347", 1: "#89C35C"}
    fill_color = {-1: "white", 1: "#89C35C"}
    line_width = {-1: 2, 1: 0}

    for ichg, d in enumerate(data):
        direction = d[-1]
        start_y = round_up(min(d[:2]), BOX_SIZE)
        end_y = round_up(max(d[:2]), BOX_SIZE) + BOX_SIZE / 100

        y = np.arange(start_y, end_y, BOX_SIZE)
        x = [ichg + 1] * len(y)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(
                    color=fill_color[direction],
                    size=8,
                    line=dict(color=color[direction], width=line_width[direction]),
                ),
                marker_symbol=symbol.get(direction),
            )
        )
    fig.update_layout(
        title_text=company_name,
        title_x=0.5,
        width=min(max(len(changes) * 20, 600), 1600),
        height=min(max((max(changes) - min(changes)) * 20, 600), 1000),
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
