import streamlit as st
import pandas as pd

def show(df):
    df = pd.read_csv(df) if isinstance(df, str) else df

    st.title("Замнал ба давтамж")

    df2 = df[['Төрөл','Тасаг','ICDCODE_NAME','ICD10 нэр']].dropna()

    #path fre
    df2['path'] = df2.apply(lambda r: (r['Төрөл'], r['Тасаг'], r['ICDCODE_NAME'], r['ICD10 нэр']), axis=1)
    path_freq = df2['path'].value_counts().reset_index()
    path_freq.columns = ['Замнал (Төрөл→Тасаг→Онош1→Онош2)','freq']

    st.subheader("Замналын давтамж (Path Frequency)")
    st.dataframe(path_freq)
    st.bar_chart(path_freq.set_index('Замнал (Төрөл→Тасаг→Онош1→Онош2)'))


    # 2. Edge fre
    edges = []
    for _, r in df2.iterrows():
        edges += [(r['Төрөл'], r['Тасаг']), (r['Тасаг'], r['ICDCODE_NAME']), (r['ICDCODE_NAME'], r['ICD10 нэр'])]
    edge_freq = pd.DataFrame(edges, columns=['source','target'])
    edge_freq = edge_freq.value_counts().reset_index()
    edge_freq.columns = ['source','target','freq']

    st.subheader("Холбооны давтамж (Edge Frequency)")
    st.dataframe(edge_freq)
    st.bar_chart(edge_freq.set_index('source')['freq'])


    # 3. Conditional Probability
    group = df2.groupby(['Төрөл', 'Тасаг', 'ICDCODE_NAME'])
    prob_list = []
    for keys, sub in group:
        total = len(sub)
        for _, row in sub.iterrows():
            prob_list.append({
                'Төрөл': keys[0],
                'Тасаг': keys[1],
                'Онош1': keys[2],
                'Онош2': row['ICD10 нэр'],
                'freq': 1,
                'probability': 1 / total
            })

    prob_df = pd.DataFrame(prob_list)
    prob_df = prob_df.groupby(['Төрөл', 'Тасаг', 'Онош1', 'Онош2'])[['freq','probability']].sum().reset_index()

    st.subheader("Магадлал — P(Онош2 | Төрөл, Тасаг, Онош1)")
    st.dataframe(prob_df)

    # onosh1 songood
    selected_onosh = st.selectbox("Онош1 сонгох:", prob_df['Онош1'].unique())
    filtered = prob_df[prob_df['Онош1'] == selected_onosh]
    st.bar_chart(filtered.set_index('Онош2')['probability'])
