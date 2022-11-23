import streamlit as st
import pandas as pd
from pnf import run_pnf_plotly

DATA_PATH = "data/bursa_data.csv"

st.set_page_config(
    page_title="Point and Figure", layout="wide",
)
st.title("Point and Figure | Bursa Malaysia")


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_PATH)

    return df


df = load_data()
names = st.multiselect(
    "company name", df["name"].unique(), default="Hartalega Holdings Bhd"
)


st.write(names)


box_size = {}
reversal = {}
for name in names:
    tdf = df[df["name"] == name]
    box_size[name] = round(tdf["px"].diff().iloc[-30:].std(), 2)
    st.markdown("<hr style='border:2px solid gray'>", True)
    st.header(name)
    reversal[name] = st.number_input(f"reversal of {name}", value=3, min_value=1)
    box_size[name] = st.number_input(
        f"box size of {name}", value=box_size[name], min_value=0.01
    )

    fig = run_pnf_plotly(tdf, box_size[name], reversal[name])
    if fig:
        st.plotly_chart(fig, use_container_width=True, height=fig.layout.height)
    else:
        st.write(
            name, ": no point and figure result, try to change box size or reversal"
        )
