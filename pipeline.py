"""
=============================================================================
Inteligência Territorial e Segurança Pública — Rio de Janeiro
=============================================================================
Autor  : Arthur Riess Cunha
Versão : 0.1.0
Fonte  : ISP-RJ (https://www.ispdados.rj.gov.br)

Fluxo principal:
    CSV bruto (data/raw/)
        → carregar_dados()
        → limpar_dados()
        → gerar_metricas()
        → analise_temporal()
        → preparar_visualizacao()
        → [FUTURO] prever_tendencia()
        → DataFrames prontos para Streamlit / Plotly
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from sklearn.linear_model import LinearRegression
from scipy import stats

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes do domínio
# ---------------------------------------------------------------------------
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

ARQUIVO_PADRAO = RAW_DIR/"BaseDPEvolucaoMensalCisp.csv"

COLUNAS_ID = ["cisp", "mes_ano", "aisp", "risp", "munic", "regiao"]

# Grupo 1 — Crimes violentos 
COLUNAS_VIOLENCIA = ["hom_doloso", "latrocinio", "cvli", "letalidade_violenta"]

# Grupo 2 — Roubos 
COLUNAS_ROUBO = ["roubo_veiculo", "roubo_celular", "roubo_transeunte", "total_roubos"]

# Grupo 3 — Drogas
COLUNAS_DROGAS = ["posse_drogas", "trafico_drogas"]

# Grupo 4 — Furtos
COLUNAS_FURTO = ["furto_celular", "furto_transeunte"]

COLUNAS_CRIME = COLUNAS_VIOLENCIA + COLUNAS_ROUBO + COLUNAS_DROGAS + COLUNAS_FURTO

# =============================================================================
# 1. CARREGAMENTO
# =============================================================================

def carregar_dados(caminho: str | Path) -> pd.DataFrame:
    
    caminho = Path(caminho)

    try:
        df = pd.read_csv(
            caminho,
            sep=";",
            encoding="latin-1",
            dtype=str,
            low_memory=False,
        )

    except FileNotFoundError:
        log.error("Arquivo não encontrado: %s", caminho)
        raise

    except pd.errors.EmptyDataError:
        log.error("O arquivo está vazio: %s", caminho)
        raise ValueError(f"Arquivo vazio: {caminho}")

    faltando = [col for col in COLUNAS_ID + COLUNAS_VIOLENCIA if col not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes no CSV: {faltando}")

    log.info("Dados carregados: %s linhas, %s colunas", *df.shape)
    return df


# =============================================================================
# 2. LIMPEZA
# =============================================================================

def limpar_dados(df, colunas_crime=None):
    if colunas_crime is None:
        colunas_crime = COLUNAS_VIOLENCIA

    df = df.copy()

    for col in ["munic", "regiao", "aisp", "cisp"]:
        df[col] = df[col].str.strip().str.upper()

    df["mes_ano"] = pd.to_datetime(df["mes_ano"], format="%Ym%m", errors="coerce")
    df["mes_ano"] = df["mes_ano"].dt.to_period("M")

    for col in colunas_crime:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df = df.melt(
        id_vars=COLUNAS_ID,
        value_vars=colunas_crime,
        var_name="tipo_crime",
        value_name="qtd_ocorrencias",
    )

    df = df.drop_duplicates(subset=["cisp", "mes_ano", "tipo_crime"])

    log.info("Limpeza concluida. Shape final: %s", df.shape)
    return df


# =============================================================================
# 3. MÉTRICAS
# =============================================================================

# Foram geradas 3 métricas para fins de análise:
# Taxa por 100k habitantes, média móvel de 3 meses e variação percentual mês a mês.

#População estimada por AISP, baseada em dados do ISP-RJ e IBGE.
# AISP são áreas de segurança pública, cada uma cobrindo vários municípios. 

POPULACAO_AISP = {
    "1":  232000,  "2":  340000,  "3":  250000,  "4":  214000,
    "5":  530000,  "6":  371000,  "7":  275000,  "9":  226000,
    "10": 195000,  "14": 417000,  "15": 364000,  "16": 389000,
    "17": 295000,  "18": 231000,  "19": 295000,  "20": 305000,
    "21": 248000,  "22": 377000,  "23": 264000,  "24": 237000,
    "25": 229000,  "26": 188000,  "27": 232000,  "28": 278000,
    "29": 316000,  "30": 275000,  "31": 196000,  "32": 228000,
    "33": 253000,  "34": 213000,  "35": 196000,  "36": 228000,
    "37": 180000,  "38": 243000,  "39": 302000,  "40": 198000,
    "41": 310000,  "43": 216000,
}

def gerar_metricas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["populacao"] = df["aisp"].map(POPULACAO_AISP)
    df["taxa_100k"] = (df["qtd_ocorrencias"] / df["populacao"]) * 100_000

    df.sort_values(["aisp", "tipo_crime", "mes_ano"], inplace=True)

    df["media_movel_3"] = (
        df.groupby(["aisp", "tipo_crime"])["qtd_ocorrencias"]
          .transform(lambda x: x.rolling(window=3, min_periods=1).mean())
    )

    df["variacao_pct"] = (
        df.groupby(["aisp", "tipo_crime"])["qtd_ocorrencias"]
          .pct_change() * 100
    )

    log.info("Métricas geradas. Shape final: %s", df.shape)
    return df


# =============================================================================
# 4. ANÁLISE TEMPORAL
# =============================================================================

def analise_temporal(
    df: pd.DataFrame,
    tipo_crime: str | None = None,
    aisp: str | None = None,
) -> pd.DataFrame:
    df = df.copy()

    if tipo_crime:
        df = df[df["tipo_crime"] == tipo_crime.lower()]

    if aisp:
        df = df[df["aisp"] == aisp.upper()]

    serie = (
        df.groupby("mes_ano")
          .agg(
              total_ocorrencias=("qtd_ocorrencias", "sum"),
              taxa_100k_media=("taxa_100k", "mean"),
              media_movel_3=("media_movel_3", "mean"),
          )
          .sort_index()
    )

    log.info(
        "Serie temporal: %s meses | crime=%s | aisp=%s",
        len(serie), tipo_crime or "todos", aisp or "todas",
    )
    return serie


# =============================================================================
# 5. PREPARAÇÃO PARA VISUALIZAÇÃO
# =============================================================================

def preparar_visualizacao(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    heatmap = df.pivot_table(
        index="aisp",
        columns="mes_ano",
        values="taxa_100k",
        aggfunc="sum",
        fill_value=0,
    )

    mes_mais_recente = df["mes_ano"].max()
    ranking = (
        df[df["mes_ano"] == mes_mais_recente]
        .groupby("aisp")["qtd_ocorrencias"]
        .sum()
        .nlargest(10)
        .reset_index()
        .rename(columns={"qtd_ocorrencias": "total_ocorrencias"})
    )

    series = analise_temporal(df)

    por_tipo = (
        df.groupby("tipo_crime")["qtd_ocorrencias"]
        .sum()
        .reset_index()
        .rename(columns={"qtd_ocorrencias": "total_ocorrencias"})
        .sort_values("total_ocorrencias", ascending=False)
    )

    resultado = {
        "heatmap":  heatmap,
        "ranking":  ranking,
        "series":   series,
        "por_tipo": por_tipo,
    }
    log.info("Visualizacao preparada. Chaves: %s", list(resultado.keys()))
    return resultado


# =============================================================================
# 6. PREVISÃO COM REGRESSÃO LINEAR
# =============================================================================

def prever_tendencia(
    serie_temporal: pd.DataFrame,
    meses_futuros: int = 3,
) -> pd.DataFrame:
    n = len(serie_temporal)

    X = np.arange(n).reshape(-1, 1)
    y = serie_temporal["total_ocorrencias"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    r2 = modelo.score(X, y)
    log.info("Regressão linear: R²=%.3f | inclinação=%.2f", r2, modelo.coef_[0])

    residuos  = y - modelo.predict(X)
    s         = np.sqrt(np.sum(residuos**2) / (n - 2))
    t_critico = stats.t.ppf(0.975, df=n - 2)
    margem    = t_critico * s

    ultimo_mes   = serie_temporal.index.max()
    periodos_fut = pd.period_range(start=ultimo_mes + 1, periods=meses_futuros, freq="M")
    X_fut        = np.arange(n, n + meses_futuros).reshape(-1, 1)
    y_fut        = modelo.predict(X_fut)

    df_futuro = pd.DataFrame(
        {
            "total_ocorrencias": np.nan,
            "taxa_100k_media":   np.nan,
            "media_movel_3":     np.nan,
            "previsao":          np.maximum(y_fut, 0).round(1),
            "intervalo_inf":     np.maximum(y_fut - margem, 0).round(1),
            "intervalo_sup":     (y_fut + margem).round(1),
        },
        index=periodos_fut,
    )
    df_futuro.index.name = "mes_ano"

    return pd.concat([serie_temporal, df_futuro])

