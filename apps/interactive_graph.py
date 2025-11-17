# apps/interactive_graph.py
import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

def show(df):
    # DataFrame эсэхийг шалгаад унших
    df = pd.read_csv(df) if isinstance(df, str) else df

    st.title("🌐 PyVis интерактив граф — Өвчтөний замнал")

    df2 = df[['Төрөл','Тасаг','ICDCODE_NAME','ICD10 нэр']].dropna()

    # Session state-д сонгосон node
    if "selected_nodes" not in st.session_state:
        st.session_state.selected_nodes = []

    # Layout 2 columns
    col1, col2 = st.columns([1, 2])

    # ---------------------------
    # LEFT FILTER PANEL
    # ---------------------------
    with col1:
        st.header("🔍 Фильтерүүд")
        f1 = st.selectbox("Төрөл", [""] + sorted(df2["Төрөл"].unique()))
        f2 = st.selectbox("Тасаг", [""] + sorted(df2["Тасаг"].unique()))
        f3 = st.selectbox("Онош1 (ICDCODE_NAME)", [""] + sorted(df2["ICDCODE_NAME"].unique()))
        f4 = st.selectbox("Онош2 (ICD10 нэр)", [""] + sorted(df2["ICD10 нэр"].unique()))

        filtered_df = df2.copy()
        if f1: filtered_df = filtered_df[filtered_df["Төрөл"]==f1]
        if f2: filtered_df = filtered_df[filtered_df["Тасаг"]==f2]
        if f3: filtered_df = filtered_df[filtered_df["ICDCODE_NAME"]==f3]
        if f4: filtered_df = filtered_df[filtered_df["ICD10 нэр"]==f4]

        st.write("Илэрсэн мөр:", len(filtered_df))

    # ---------------------------
    # CENTER — PYVIS GRAPH
    # ---------------------------
    with col2:
        st.header("📌 Интерактив Graph")

        # Edge Frequency үүсгэх
        edges = []
        for _, r in filtered_df.iterrows():
            edges += [
                (r['Төрөл'], r['Тасаг'], 'orange'),
                (r['Тасаг'], r['ICDCODE_NAME'], 'green'),
                (r['ICDCODE_NAME'], r['ICD10 нэр'], 'red')
            ]
        edge_df = pd.DataFrame(edges, columns=['source','target','color'])
        edge_freq = edge_df.value_counts().reset_index()
        edge_freq.columns = ['source','target','freq','color']

        # PyVis граф
        net = Network(height="700px", width="100%", directed=True, bgcolor="#222222", font_color="white")
        for _, row in edge_freq.iterrows():
            net.add_node(row['source'], label=row['source'], color=row['color'])
            net.add_node(row['target'], label=row['target'], color=row['color'])
            net.add_edge(row['source'], row['target'], value=row['freq'], title=f"{row['source']} → {row['target']}")

        # HTML хадгалах, render
        net.save_graph("graph.html")
        with open("graph.html",'r',encoding='utf-8') as f:
            html = f.read()

        # JS event оруулах (сонгосон node-г харуулах alert)
        custom_js = """
        <script>
        document.addEventListener("DOMContentLoaded", function () {
            var network = window.network;
            if(network){
                network.on("selectNode", function(params){
                    var node_id = params.nodes[0];
                    alert("Сонгосон node → " + node_id);
                });
            }
        });
        </script>
        """
        components.html(custom_js + html, height=780)
