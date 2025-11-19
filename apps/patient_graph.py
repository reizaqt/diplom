import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

def show(df):
    df = pd.read_csv(df) if isinstance(df, str) else df
    df['Огноо'] = pd.to_datetime(df['Огноо'], errors='coerce')
    df['Year'] = df['Огноо'].dt.year

    st.title("Өвчтөний бүх замналын дүрслэл")

    years = sorted(df['Year'].dropna().unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Огноо", years, index=0)

    departments = ["Бүх тасаг"] + sorted(df['Тасаг'].dropna().unique())
    selected_dep = st.sidebar.selectbox("Тасаг сонгох", departments)

    filtered_df = df[df['Year'] >= selected_year]
    if selected_dep != "Бүх тасаг":
        filtered_df = filtered_df[filtered_df['Тасаг'] == selected_dep]

    st.sidebar.markdown(f"**Нийт :** {len(filtered_df)}")

    G = nx.DiGraph()
    patients = filtered_df['Иргэний ID']
    colors = list(mcolors.CSS4_COLORS.keys())
    random.shuffle(colors)
    patient_color_map = {pid: colors[i % len(colors)] for i, pid in enumerate(patients)}

    for _, row in filtered_df.iterrows():
        patient_node = f"Өвчтөн_{row['Иргэний ID']}"
        hospital_node = f"{row['Эмнэлэг']} ({row['Аймаг нийслэл']}, {row['Сум дүүрэг']})"
        type_dep_node = f"{row['Төрөл']} - {row['Тасаг']}"
        diagnosis1_node = row['ICDCODE_NAME']
        diagnosis2_node = row['ICD10 нэр']

        G.add_node(patient_node, type='patient', color=patient_color_map[row['Иргэний ID']])
        G.add_node(hospital_node, type='hospital', color='lightgreen')
        G.add_node(type_dep_node, type='type_dep', color='orange')
        G.add_node(diagnosis1_node, type='diagnosis', color='pink')
        if pd.notna(diagnosis2_node) and diagnosis2_node != '':
            G.add_node(diagnosis2_node, type='diagnosis', color='red')

        G.add_edge(patient_node, hospital_node)
        G.add_edge(hospital_node, type_dep_node)
        G.add_edge(type_dep_node, diagnosis1_node)
        if pd.notna(diagnosis2_node) and diagnosis2_node != '':
            G.add_edge(diagnosis1_node, diagnosis2_node)

    node_shapes = {'patient': 'o', 'hospital': 's', 'type_dep': 'D', 'diagnosis': '^'}
    fig, ax = plt.subplots(figsize=(18, 12))
    pos = nx.spring_layout(G, k=0.6, seed=42)
    for ntype, shape in node_shapes.items():
        nodes = [n for n, a in G.nodes(data=True) if a['type'] == ntype]
        colors_ = [G.nodes[n]['color'] for n in nodes]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=colors_, node_shape=shape, node_size=800, alpha=0.9)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=15, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=7)
    plt.title(f"Өвчтөн замналын граф — {selected_year} оноос хойш", fontsize=13)
    plt.axis('off')
    st.pyplot(fig)
