import streamlit as st
import pandas as pd
import plotly.express as px

from pipeline import (
    ARQUIVO_PADRAO, carregar_dados, limpar_dados, gerar_metricas,
    COLUNAS_VIOLENCIA, COLUNAS_ROUBO, COLUNAS_DROGAS, COLUNAS_FURTO,
)

st.set_page_config(
    page_title="ISP-RJ — Segurança Pública",
    page_icon="🔍",
    layout="wide",
)


LABELS_CRIME = {
    # Violência
    "hom_doloso":          "Homicídio Doloso",
    "latrocinio":          "Latrocínio",
    "cvli":                "CVLI",
    "letalidade_violenta": "Letalidade Violenta",
    # Roubo
    "roubo_veiculo":       "Roubo de Veículo",
    "roubo_celular":       "Roubo de Celular",
    "roubo_transeunte":    "Roubo a Transeunte",
    "total_roubos":        "Total de Roubos ⚠️",
    # Drogas
    "posse_drogas":        "Posse de Drogas",
    "trafico_drogas":      "Tráfico de Drogas",
    # Furto
    "furto_celular":       "Furto de Celular",
    "furto_transeunte":    "Furto a Transeunte",
}

GRUPOS_CRIME = {
    "Violência": COLUNAS_VIOLENCIA,
    "Roubo":     COLUNAS_ROUBO,
    "Drogas":    COLUNAS_DROGAS,
    "Furto":     COLUNAS_FURTO,
}

AISP_REGIOES = {
    1:  "Centro, Gamboa, Saúde, Santo Cristo (5º BPM)",
    2:  "Botafogo, Flamengo, Laranjeiras, Catete, Urca (2º BPM)",
    3:  "Méier, Engenho de Dentro, Piedade, Todos os Santos (3º BPM)",
    4:  "São Cristóvão, Benfica, Mangueira (4º BPM)",
    5:  "Praça Mauá, Porto Maravilha (13º BPM)",
    6:  "Tijuca, Grajaú, Vila Isabel, Andaraí (6º BPM)",
    7:  "São Gonçalo (7º BPM)",
    8:  "Campos dos Goytacazes, São João da Barra, S. F. de Itabapoana (8º BPM)",
    9:  "Rocha Miranda, Madureira, Marechal Hermes, Honório Gurgel (9º BPM)",
    10: "Barra do Piraí, Valença, Vassouras, Piraí (10º BPM)",
    11: "Nova Friburgo, Bom Jardim, Cantagalo (11º BPM)",
    12: "Niterói e Maricá (12º BPM)",
    13: "Cabo Frio, Búzios, Arraial do Cabo, São Pedro da Aldeia (25º BPM)",
    14: "Bangu, Realengo, Padre Miguel, Magalhães Bastos (14º BPM)",
    15: "Duque de Caxias (15º BPM)",
    16: "Olaria, Penha, Ramos, Cordovil (16º BPM)",
    17: "Ilha do Governador (17º BPM)",
    18: "Jacarepaguá, Taquara, Curicica, Cidade de Deus (18º BPM)",
    19: "Copacabana e Leme (19º BPM)",
    20: "Nova Iguaçu, Mesquita, Nilópolis (20º BPM)",
    21: "São João de Meriti (21º BPM)",
    22: "Maré, Bonsucesso (22º BPM)",
    23: "Leblon, Ipanema, Gávea, São Conrado, Rocinha (23º BPM)",
    24: "Queimados, Japeri, Paracambi, Itaguaí, Seropédica (24º BPM)",
    25: "Cabo Frio e Região dos Lagos (Administrativo 25º BPM)",
    26: "Petrópolis (26º BPM)",
    27: "Santa Cruz, Sepetiba, Paciência (27º BPM)",
    28: "Volta Redonda, Barra Mansa, Pinheiral (28º BPM)",
    29: "Itaperuna, Cardoso Moreira, Italva (29º BPM)",
    30: "Teresópolis, Guapimirim, Carmo (30º BPM)",
    31: "Barra da Tijuca, Recreio dos Bandeirantes, Itanhangá (31º BPM)",
    32: "Macaé, Rio das Ostras, Casimiro de Abreu (32º BPM)",
    33: "Angra dos Reis, Mangaratiba (33º BPM)",
    34: "Magé, Guapimirim (34º BPM)",
    35: "Itaboraí, Tanguá, Rio Bonito (35º BPM)",
    36: "Santo Antônio de Pádua, Miracema, Aperibé (36º BPM)",
    37: "Resende, Itatiaia, Porto Real, Quatis (37º BPM)",
    38: "Três Rios, Paraíba do Sul, Sapucaia (38º BPM)",
    39: "Belford Roxo (39º BPM)",
    40: "Campo Grande, Cosmos, Santíssimo (40º BPM)",
    41: "Pavuna, Costa Barros, Ricardo de Albuquerque (41º BPM)",
    42: "Mesquita e Nilópolis - Desmembramento (20º BPM)",
    43: "Duque de Caxias - Desmembramento (15º BPM)",
}

# Serve para carregar e processar os dados uma única vez, e depois usar o resultado em toda a aplicação sem recarregar ou recalcular.

@st.cache_data
def carregar_pipeline() -> pd.DataFrame:
    df = carregar_dados(ARQUIVO_PADRAO)
    df = limpar_dados(df, colunas_crime=COLUNAS_VIOLENCIA + COLUNAS_ROUBO + COLUNAS_DROGAS + COLUNAS_FURTO)
    df = gerar_metricas(df)
    df["ano"] = df["mes_ano"].dt.year
    return df


df_raw = carregar_pipeline()

aisps_ord = sorted(df_raw["aisp"].unique(), key=int)
tipos_ord = sorted(df_raw["tipo_crime"].unique())
anos_ord  = sorted(df_raw["ano"].unique())

# SIDEBAR

with st.sidebar:
    st.title("Filtros")

    st.markdown("**Período**")
    ano_ini, ano_fim = st.select_slider(
        "periodo_label",
        options=anos_ord,
        value=(anos_ord[0], anos_ord[-1]),
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**AISP**")
    aisps_sel = st.multiselect(
        "aisps_label",
        options=aisps_ord,
        default=aisps_ord,
        placeholder="Selecione AISPs…",
        label_visibility="collapsed",
    )

    aisps_exibir = aisps_sel or aisps_ord
    with st.expander(f" Regiões ({len(aisps_exibir)} AISPs)"):
        for aisp in sorted(aisps_exibir, key=int):
            descricao = AISP_REGIOES.get(int(aisp), "—")
            st.markdown(f"**{aisp}** — {descricao}")

    st.divider()

    st.markdown("**Grupo de Crime**")
    grupos_sel = st.multiselect(
        "grupos_label",
        options=list(GRUPOS_CRIME.keys()),
        default=list(GRUPOS_CRIME.keys()),
        placeholder="Selecione grupos…",
        label_visibility="collapsed",
    )

    grupos_ativos = grupos_sel or list(GRUPOS_CRIME.keys())
    tipos_do_grupo = [t for g in grupos_ativos for t in GRUPOS_CRIME[g]]

    st.markdown("**Tipo de Crime**")
    tipos_sel = st.multiselect(
        "tipos_label",
        options=tipos_do_grupo,
        default=tipos_do_grupo,
        format_func=lambda x: LABELS_CRIME.get(x, x),
        placeholder="Selecione tipos…",
        label_visibility="collapsed",
    )

# FILTROS

aisps_ativos = aisps_sel or aisps_ord
tipos_ativos = tipos_sel or tipos_do_grupo

df = df_raw[
    df_raw["aisp"].isin(aisps_ativos)
    & df_raw["tipo_crime"].isin(tipos_ativos)
    & df_raw["ano"].between(ano_ini, ano_fim)
].copy()

# PÁGINA

st.title("Segurança Pública — Rio de Janeiro")

if df.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

_individuais_roubo = {"roubo_veiculo", "roubo_celular", "roubo_transeunte"}
if "total_roubos" in tipos_ativos and _individuais_roubo & set(tipos_ativos):
    st.warning(
        "**Atenção — dupla contagem:** 'Total de Roubos ⚠️' já inclui "
        "Roubo de Veículo, Celular e Transeunte. "
        "Desmarque os tipos individuais ou o total para evitar contagem duplicada."
    )

# SÉRIE TEMPORAL

col_titulo, col_toggle = st.columns([5, 2])
with col_titulo:
    st.subheader("Evolução Mensal de Ocorrências")
with col_toggle:
    metrica = st.radio(
        "metrica_label",
        options=["Total", "Média Móvel (3m)"],
        horizontal=True,
        label_visibility="collapsed",
    )

# Agrega por mês e calcula média móvel sobre o total (não média de médias)
serie = (
    df.groupby("mes_ano", as_index=False)["qtd_ocorrencias"]
    .sum()
    .sort_values("mes_ano")
)
serie["mes_str"]      = serie["mes_ano"].astype(str)
serie["media_movel_3"] = serie["qtd_ocorrencias"].rolling(window=3, min_periods=1).mean().round(1)

usar_media = metrica == "Média Móvel (3m)"
y_col  = "media_movel_3"    if usar_media else "qtd_ocorrencias"
label_y = "Média Móvel 3m"  if usar_media else "Total de Ocorrências"
cor    = "#457B9D"           if usar_media else "#E63946"

fig = px.line(
    serie,
    x="mes_str",
    y=y_col,
    labels={"mes_str": "Mês", y_col: label_y},
    color_discrete_sequence=[cor],
)
fig.update_traces(
    hovertemplate=f"{label_y}: %{{y:,.0f}}<extra></extra>",
    **({"line_dash": "dash"} if usar_media else {}),
)

fig.update_layout(
    xaxis_tickangle=-45,
    hovermode="x unified",
    height=430,
    showlegend=False,
    margin=dict(l=0, r=10, t=30, b=0),
)
st.plotly_chart(fig, use_container_width=True)

# Métricas de resumo
# Total e média sempre refletem os dados reais; pico e mês do pico seguem o toggle

total_real = int(serie["qtd_ocorrencias"].sum())
media_real = serie["qtd_ocorrencias"].mean()
pico       = serie[y_col].max()
mes_pico   = serie.loc[serie[y_col].idxmax(), "mes_str"]

fmt_pico = "{:,.1f}" if usar_media else "{:,.0f}"
label_pico = "Pico mensal (MM3)" if usar_media else "Pico mensal"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total real no período", f"{total_real:,}")
c2.metric("Média mensal real",     f"{media_real:,.0f}")
c3.metric(label_pico,              fmt_pico.format(pico))
c4.metric("Mês do pico",          mes_pico)
