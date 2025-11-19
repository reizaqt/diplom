import streamlit as st
from apps import patient_graph, path_frequency, interactive_graph
import pandas as pd

st.set_page_config(page_title="Эрүүл мэндийн анализ", layout="wide")

menu = ["Өвчтөний замналын дүрслэл", 
        "Замнал ба давтамж", 
        "Өвчтөний замналын граф"]
choice = st.sidebar.selectbox("Select page", menu)

if 'data' not in st.session_state:
    uploaded = st.file_uploader("CSV файл сонгоно уу", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state['data'] = df
        st.success("Файл амжилттай")
else:
    df = st.session_state['data']

if 'data' in st.session_state:
    df = st.session_state['data']
    if choice == menu[0]:
        patient_graph.show(df)
    elif choice == menu[1]:
        path_frequency.show(df)
    elif choice == menu[2]:
        interactive_graph.show(df)
else:
    st.info("Заавал CSV файлаа заана уу")
