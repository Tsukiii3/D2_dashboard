import pandas as pd
import streamlit as st
import plotly.express as px
import re
import gspread
from google.oauth2.service_account import Credentials
from gspread import spreadsheet

# ================= CONFIG =================
st.set_page_config(
    page_title='DATA DESTINY ACTIVITIES',
    page_icon='🎮',
    layout='wide'
)
# ================= TEMA =================
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
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0px 0px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

# ================= DADOS =================

@st.cache_data(ttl=300)
def carregar_dados():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope,
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(
        "1pkDTOC38D5rFlBbCBAAAOC3qEMVa6y-8hsy_KH_A2x0"
    )
    def aba_para_df(gid):
        worksheet = spreadsheet.get_worksheet_by_id(gid)
        data = worksheet.get_all_values()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])
    df_modos = aba_para_df(1922820478)
    df_raids = aba_para_df(1252752604)
    df_masmorras = aba_para_df(1143212602)

    return df_modos, df_raids, df_masmorras

df_modos, df_raids, df_masmorras = carregar_dados()

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

for df in [df_raids, df_masmorras]:
    df['Conclusão_Mais_Rápida_seg'] = df['Conclusão_Mais_Rápida'].apply(tempo_para_segundos)
    df['Média_Tempo_seg'] = df['Média_Tempo'].apply(tempo_para_segundos)

st.markdown("""
<h1 style="text-align:center;">TSUKII#5231</h1>
""", unsafe_allow_html=True)

total_horas = df_modos['Horas'].sum()
total_kills = df_modos['Total_Kills'].sum()
total_atividades = df_modos['Quantidade_feita'].sum()

t1, t2, t3 = st.columns(3)

df_modos["Horas_Jogadas"] = pd.to_numeric(df_modos["Horas_Jogadas"], errors="coerce")
df_modos["Horas_Jogadas"] = df_modos["Horas_Jogadas"].fillna(0)
t2.metric("Total Kills", f"{int(total_kills)}")
t3.metric("Atividades", f"{int(total_atividades)}")

st.divider()

st.header("DESTINY STATUS")
st.markdown("### Filtros")

f1, f2, f3 = st.columns(3)

with f1:
    modo_selecionado = st.selectbox(
        "Modo",
        ['Todos'] + sorted(df_modos['Modo'].dropna().unique()),
        key="modo_select"
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
        ],
        key="metrica_modo"
    )
with f3:
    ordem_status = st.radio(
        "Ordenação",
        ["Maior → Menor", "Menor → Maior"],
        key="ordem_status"
    )
if modo_selecionado == 'Todos':
    df_fill = df_modos.copy()
else:
    df_fill = df_modos[df_modos['Modo'] == modo_selecionado]
asc = ordem_status == "Menor → Maior"

df_fill = df_fill.sort_values(
    by=metrica,
    ascending=asc
)
g1, g2 = st.columns([2, 1])

with g1:
    fig_bar = px.bar(
        df_fill,
        x='Modo',
        y=metrica,
        text=metrica,
        title=f'{metrica} por Modo'
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        xaxis_title="Modo",
        yaxis_title=metrica
    )
    st.plotly_chart(fig_bar, use_container_width=True)
with g2:
    fig_pie = px.pie(
        df_fill,
        names='Modo',
        values=metrica,
        title='Distribuição (%)',
        hole=0.4
    )
    fig_pie.update_traces(
        textinfo='percent+label'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.header("RAIDS")
st.markdown("### Filtros Raid")

r1, r2, r3 = st.columns(3)

with r1:
    raid_selecionada = st.selectbox(
        "Raid",
        ['Todos'] + sorted(df_raids['Raid_Nome'].dropna().unique()),
        key="raid_select"
    )
with r2:
    metrica_raid = st.selectbox(
        "Métrica",
        [
            'Conclusões',
            'Sherpas',
            'Conclusão_Mais_Rápida',
            'Média_Tempo'
        ],
        key="metrica_raid"
    )
with r3:
    ordem_raid = st.radio(
        "Ordenação",
        ["Maior → Menor", "Menor → Maior"],
        key="ordem_raid"
    )
if raid_selecionada == 'Todos':
    df_fill = df_raids.copy()
else:
    df_fill = df_raids[df_raids['Raid_Nome'] == raid_selecionada]
asc = ordem_raid == "Menor → Maior"
is_tempo = metrica_raid in ['Conclusão_Mais_Rápida', 'Média_Tempo']

if is_tempo:
    coluna = metrica_raid + '_seg'
    df_fill = df_fill.sort_values(coluna, ascending=asc)

    fig = px.bar(
        df_fill,
        x='Raid_Nome',
        y=coluna,
        text=metrica_raid,
        title=f'{metrica_raid} por Raid (segundos)'
    )
    fig.update_yaxes(title="Tempo (s)")
else:
    df_fill = df_fill.sort_values(metrica_raid, ascending=asc)
    fig = px.bar(
        df_fill,
        x='Raid_Nome',
        y=metrica_raid,
        text=metrica_raid,
        title=f'{metrica_raid} por Raid'
    )
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

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
asc = ordem_masmorra == "Menor → Maior"
is_tempo = metrica_masmorras in ['Conclusão_Mais_Rápida', 'Média_Tempo']

if is_tempo:
    coluna = metrica_masmorras + '_seg'
    df_fill = df_fill.sort_values(coluna, ascending=asc)
    fig = px.bar(
        df_fill,
        x='Dungeon_nome',
        y=coluna,
        text=metrica_masmorras,
        title=f'{metrica_masmorras} por Masmorra (segundos)'
    )
    fig.update_yaxes(title="Tempo (s)")
else:
    df_fill = df_fill.sort_values(metrica_masmorras, ascending=asc)
    fig = px.bar(
        df_fill,
        x='Dungeon_nome',
        y=metrica_masmorras,
        text=metrica_masmorras,
        title=f'{metrica_masmorras} por Masmorra'
    )
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)