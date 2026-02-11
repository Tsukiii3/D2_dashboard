import pandas as pd
import streamlit as st
import plotly.express as px
import re

st.set_page_config(
    page_title='DATA DESTINY ACTIVITIES',
    page_icon='🎮',
    layout='wide'
)
modo_tema = st.sidebar.radio("🌗 Tema", ["Dark", "Light"])


if modo_tema == "Light":

    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f7fa;
            color: #111111;
        }
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
        }
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #111111 !important;
        }
        input, textarea, select {
            background-color: #ffffff !important;
            color: black !important;
        }
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0px 0px 5px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1pkDTOC38D5rFlBbCBAAAOC3qEMVa6y-8hsy_KH_A2x0"

GID_MODOS = "1922820478"
GID_RAIDS = "1252752604"
GID_MASMORRAS = "1143212602"

URL_MODOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_MODOS}"
URL_RAIDS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_RAIDS}"
URL_MASMORRAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_MASMORRAS}"

@st.cache_data(ttl=300)
def carregar_dados():
    df_modos = pd.read_csv(URL_MODOS)
    df_raids = pd.read_csv(URL_RAIDS)
    df_masmorras = pd.read_csv(URL_MASMORRAS)

    return df_modos, df_raids, df_masmorras
df_modos, df_raids, df_masmorras = carregar_dados()

st.sidebar.title("DESTINY DASHBOARD")

if st.sidebar.button("Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

total_kills = df_modos['Total_Kills'].sum()
total_horas = df_modos['Horas'].sum()
total_quantidade = df_modos['Quantidade_feita'].sum()

col1, col2, col3 = st.columns(3)

col1.metric(" Total Kills", f"{total_kills}")
col2.metric("⏱Horas Jogadas", f"{total_horas:.2f}")
col3.metric("Atividades", f"{total_quantidade}")

st.subheader("Destaques Gerais")

melhor_modo = df_modos.loc[df_modos['Horas'].idxmax()]
mais_kills = df_modos.loc[df_modos['Total_Kills'].idxmax()]
mais_partidas = df_modos.loc[df_modos['Quantidade_feita'].idxmax()]

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Mais Tempo",
        melhor_modo["Modo"],
        f"{melhor_modo['Horas']:.1f}h"
    )
with c2:
    st.metric(
        "Mais Kills",
        mais_kills["Modo"],
        f"{mais_kills['Total_Kills']}"
    )
with c3:
    st.metric(
        "Mais Jogado",
        mais_partidas["Modo"],
        f"{mais_partidas['Quantidade_feita']}x"
    )
st.header("DESTINY STATUS")

modos = ['Todos'] + sorted(df_modos['Modo'].dropna().unique())
modo_selecionado = st.sidebar.selectbox("Modo", modos)

metricas = [
    'Quantidade_feita',
    'Horas',
    'Win_Rate',
    'Média_Kills',
    'Média_Mortes',
    'Total_Kills',
    'Pontuação'
]

metrica = st.sidebar.selectbox("Métrica", metricas)

if modo_selecionado == 'Todos':
    df_fill = df_modos.copy()
else:
    df_fill = df_modos[df_modos['Modo'] == modo_selecionado]

fig = px.bar(
    df_fill,
    x='Modo',
    y=metrica,
    text=metrica,
    title=f'{metrica} por Modo'
)
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

st.header("⚔️ RAIDS")

raids = ['Todos'] + sorted(df_raids['Raid_Nome'].dropna().unique())
raid_selecionada = st.sidebar.selectbox("Raid", raids)

metricas_raids = [
    'Conclusões',
    'Sherpas',
    'Conclusão_Mais_Rápida',
    'Média_Tempo'
]
metrica_raid = st.sidebar.selectbox("Métrica Raid", metricas_raids)

if raid_selecionada == 'Todos':
    df_fill = df_raids.copy()
else:
    df_fill = df_raids[df_raids['Raid_Nome'] == raid_selecionada]

if metrica_raid in ['Conclusão_Mais_Rápida', 'Média_Tempo']:
    df_fill = df_fill.sort_values(by=metrica_raid)
else:
    df_fill = df_fill.sort_values(by=metrica_raid, ascending=False)

fig = px.bar(
    df_fill,
    x='Raid_Nome',
    y=metrica_raid,
    text=metrica_raid,
    title=f'{metrica_raid} por Raid'
)
if metrica_raid in ['Conclusão_Mais_Rápida', 'Média_Tempo']:
    fig.update_yaxes(autorange="reversed")

fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

st.subheader("Ranking - Top 5 Conclusões")
ordem_ranking = st.sidebar.radio(
    "📊 Ordem do Ranking",
    ["Maior → Menor", "Menor → Maior"]
)
# Garante que é número
df_raids["Conclusões"] = pd.to_numeric(
    df_raids["Conclusões"],
    errors="coerce"
).fillna(0)

if ordem_ranking == "Maior → Menor":
    asc = False
else:
    asc = True

ranking_raids = (
    df_raids
    .sort_values(by="Conclusões", ascending=asc)
    .reset_index(drop=True)
    .head(5)
)
st.dataframe(
    ranking_raids[["Raid_Nome", "Conclusões"]],
    use_container_width=True
)
st.header("MASMORRAS")

def tempo_para_segundos(tempo):

    if pd.isna(tempo):
        return 0

    tempo = str(tempo).lower()

    h = re.search(r'(\d+)h', tempo)
    m = re.search(r'(\d+)m', tempo)
    s = re.search(r'(\d+)s', tempo)

    horas = int(h.group(1)) if h else 0
    minutos = int(m.group(1)) if m else 0
    segundos = int(s.group(1)) if s else 0

    return horas * 3600 + minutos * 60 + segundos

df_masmorras['Conclusão_Mais_Rápida_seg'] = (
    df_masmorras['Conclusão_Mais_Rápida']
    .apply(tempo_para_segundos)
)
df_masmorras['Média_Tempo_seg'] = (
    df_masmorras['Média_Tempo']
    .apply(tempo_para_segundos)
)
masmorras = ['Todos'] + sorted(df_masmorras['Dungeon_nome'].dropna().unique())
masmorra_selecionada = st.sidebar.selectbox("Masmorra", masmorras)

metricas_masmorras = [
    'Conclusões',
    'Sherpas',
    'Conclusão_Mais_Rápida',
    'Média_Tempo'
]
metrica_masmorras = st.sidebar.selectbox(
    "Métrica Masmorra",
    metricas_masmorras
)
if masmorra_selecionada == 'Todos':
    df_fill = df_masmorras.copy()
else:
    df_fill = df_masmorras[
        df_masmorras['Dungeon_nome'] == masmorra_selecionada
    ]
if metrica_masmorras in ['Conclusão_Mais_Rápida', 'Média_Tempo']:
    df_fill = df_fill.sort_values(by=metrica_masmorras + '_seg')
else:
    df_fill = df_fill.sort_values(by=metrica_masmorras, ascending=False)

fig = px.bar(
    df_fill,
    x='Dungeon_nome',
    y=metrica_masmorras,
    text=metrica_masmorras,
    title=f'{metrica_masmorras} por Masmorra'
)
if metrica_masmorras in ['Conclusão_Mais_Rápida', 'Média_Tempo']:
    fig.update_yaxes(autorange="reversed")

fig.update_traces(textposition='outside')

st.plotly_chart(fig, use_container_width=True)

st.header(" Distribuição do Tempo por Atividade")

df_tempo = (
    df_modos
    .groupby('Modo', as_index=False)['Horas']
    .sum()
)

df_tempo['Porcentagem'] = (
    df_tempo['Horas'] / df_tempo['Horas'].sum()
) * 100

fig_pizza = px.pie(
    df_tempo,
    names='Modo',
    values='Horas',
    title='Porcentagem de Tempo por Atividade',
    hole=0.4
)

fig_pizza.update_traces(
    textinfo='percent+label'
)

st.plotly_chart(fig_pizza, use_container_width=True)
