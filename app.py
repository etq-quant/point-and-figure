import streamlit as st
import pandas as pd
from pnf import run_pnf_plotly

DATA_PATH = "data/bursa_data.csv"


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_PATH)

    return df


df = load_data()
names = st.multiselect(
    "company name", df["name"].unique(), default="Hartalega Holdings Bhd"
)
box_size = st.number_input("box size", value=0.1)
reversal = st.number_input("reversal", value=3)
st.write(names)

for name in names:
    tdf = df[df["name"] == name]
    fig = run_pnf_plotly(tdf, box_size, reversal)
    if fig:
        st.plotly_chart(fig)
    else:
        st.write(name, ": no point and figure result")
Hartalega Holdings Bhd