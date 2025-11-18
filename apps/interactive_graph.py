import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

def show(df):
    df = pd.read_csv(df) if isinstance(df, str) else df
    st.title("🌐 Интерактив өвчтөний замнал — PyVis Graph")

    df2 = df[['Төрөл','Тасаг','ICDCODE_NAME','ICD10 нэр']].dropna()

    if "selected_nodes" not in st.session_state:
        st.session_state.selected_nodes = []

    col1, col2 = st.columns([1, 2])

    # --------- FILTER ----------
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

        st.markdown(f"**Илэрсэн мөр:** {len(filtered_df)}")

    # --------- PYVIS GRAPH ----------
    with col2:
        st.header("📌 Интерактив Graph")

        edges = []
        for _, r in filtered_df.iterrows():
            edges += [
                (r['Төрөл'], r['Тасаг'], 'orange'),
                (r['Тасаг'], r['ICDCODE_NAME'], 'green'),
                (r['ICDCODE_NAME'], r['ICD10 нэр'], 'red')
            ]

        edge_df = pd.DataFrame(edges, columns=['source','target','color'])
        edge_freq = edge_df.groupby(['source','target','color']).size().reset_index(name='freq')

        net = Network(
            height="700px",
            width="100%",
            directed=True,
            bgcolor="#ffffff",  # цэвэрхэн background
            font_color="#000000"  # хар font
        )

        nodes_added = set()
        for _, row in edge_freq.iterrows():
            for n in [row['source'], row['target']]:
                if n not in nodes_added:
                    net.add_node(
                        n,
                        label=n,
                        color="#97C2FC",  # default blue, edge-н өнгө биш
                        shape="dot",
                        size=20,
                        shadow=True
                    )
                    nodes_added.add(n)

            net.add_edge(
                row['source'],
                row['target'],
                value=row['freq'],
                title=f"{row['source']} → {row['target']} : {row['freq']}",
                color=row['color'],
                arrows="to",
                smooth={"type": "straight"}  # шууд сум
            )

        net.set_options("""
{
  "nodes": { "font": { "size": 18 } },
  "edges": { "font": { "size": 14 } },
  "interaction": { "hover": true, "zoomView": true, "dragNodes": true, "dragView": true }
}
""")

        net.save_graph("graph.html")
        with open("graph.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=780)
