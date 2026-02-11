import pandas as pd
import streamlit as st
import plotly.express as px
import re

st.set_page_config(
    page_title='DATA DESTINY ACTIVITIES',
    page_icon='🎮',
    layout='wide'
)
modo_tema = st.sidebar.radio("Tema", ["Dark", "Light"])


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

st.header("DESTINY STATUS")

st.markdown("### 🎯 Filtros")

f1, f2 = st.columns(2)

with f1:
    modo_selecionado = st.selectbox(
        "Modo",
        ['Todos'] + sorted(df_modos['Modo'].dropna().unique())
    )
with f2:
    metrica = st.selectbox(
        "Métrica",
        [
            'Quantidade_feita',
            'Horas',
            'Win_Rate',
            'Média_Kills',
            'Média_Mortes',
            'Total_Kills',
            'Pontuação'
        ]
    )
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

st.header("RAIDS")

st.markdown("### Filtros Raid")

r1, r2, r3 = st.columns(3)
with r1:
    raid_selecionada = st.selectbox(
        "Raid",
        ['Todos'] + sorted(df_raids['Raid_Nome'].dropna().unique())
    )
with r2:
    metrica_raid = st.selectbox(
        "Métrica",
        [
            'Conclusões',
            'Sherpas',
            'Conclusão_Mais_Rápida',
            'Média_Tempo'
        ]
    )
with r3:
    ordem = st.selectbox(
        "Ordenar Ranking",
        ["Maior → Menor", "Menor → Maior"]
    )
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

st.subheader("Ranking de Raids (Conclusões)")
df_raids["Conclusões"] = pd.to_numeric(
    df_raids["Conclusões"],
    errors="coerce"
).fillna(0)
if ordem == "Maior → Menor":
    asc = False
else:
    asc = True
ranking_raids = (
    df_raids
    .sort_values(by="Conclusões", ascending=asc)
    .reset_index(drop=True)
)
ranking_raids.insert(
    0,
    "Posição",
    range(1, len(ranking_raids) + 1)
)
ranking_raids = ranking_raids[
    ["Posição", "Raid_Nome", "Conclusões"]
]
st.dataframe(
    ranking_raids,
    use_container_width=True,
    hide_index=True
)
st.header("MASMORRAS")
st.markdown("### Filtros Masmorra")

m1, m2, m3 = st.columns(3)
with m1:
    masmorra_selecionada = st.selectbox(
        "Masmorra",
        ['Todos'] + sorted(df_masmorras['Dungeon_nome'].dropna().unique()),
        key="masmorra_select"
    )
with m2:
    metrica_masmorras = st.selectbox(
        "Métrica",
        [
            'Conclusões',
            'Sherpas',
            'Conclusão_Mais_Rápida',
            'Média_Tempo'
        ],
        key="metrica_masmorra"
    )
with m3:
    ordem_masmorra = st.radio(
        "Ordenação",
        ["Maior → Menor", "Menor → Maior"],
        key="ordem_masmorra"
    )
if masmorra_selecionada == 'Todos':
    df_fill = df_masmorras.copy()
else:
    df_fill = df_masmorras[
        df_masmorras['Dungeon_nome'] == masmorra_selecionada
    ]
if ordem_masmorra == "Maior → Menor":
    asc = False
else:
    asc = True
is_tempo = metrica_masmorras in [
    'Conclusão_Mais_Rápida',
    'Média_Tempo'
]
if is_tempo:
    coluna_seg = metrica_masmorras + '_seg'
    df_fill = df_fill.sort_values(
        by=coluna_seg,
        ascending=asc
    )
    fig = px.bar(
        df_fill,
        x='Dungeon_nome',
        y=coluna_seg,
        text=metrica_masmorras,
        title=f'{metrica_masmorras} por Masmorra (em segundos)'
    )
    fig.update_yaxes(
        title="Tempo (segundos)"
    )
else:
    df_fill = df_fill.sort_values(
        by=metrica_masmorras,
        ascending=asc
    )
    fig = px.bar(
        df_fill,
        x='Dungeon_nome',
        y=metrica_masmorras,
        text=metrica_masmorras,
        title=f'{metrica_masmorras} por Masmorra'
    )
fig.update_traces(
    textposition='outside'
)
fig.update_layout(
    xaxis_title="Masmorra",
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)
st.plotly_chart(fig, use_container_width=True)