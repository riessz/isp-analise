
import pandas as pd
import pytest

from pipeline import (
    COLUNAS_ID,
    COLUNAS_VIOLENCIA,
    analise_temporal,
    carregar_dados,
    gerar_metricas,
    limpar_dados,
    prever_tendencia,
)

# carregar_dados

class TestCarregarDados:
    def test_retorna_dataframe(self, csv_valido):
        df = carregar_dados(csv_valido)
        assert isinstance(df, pd.DataFrame)

    def test_colunas_obrigatorias_presentes(self, csv_valido):
        df = carregar_dados(csv_valido)
        for col in COLUNAS_ID + COLUNAS_VIOLENCIA:
            assert col in df.columns, f"coluna ausente: {col}"

    def test_arquivo_inexistente_lanca_erro(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            carregar_dados(tmp_path / "nao_existe.csv")

    def test_colunas_faltando_lanca_valor_error(self, csv_colunas_faltando):
        with pytest.raises(ValueError, match="Colunas ausentes"):
            carregar_dados(csv_colunas_faltando)

    def test_arquivo_vazio_lanca_valor_error(self, tmp_path):
        vazio = tmp_path / "vazio.csv"
        vazio.write_bytes(b"")
        with pytest.raises(ValueError, match="vazio"):
            carregar_dados(vazio)


# limpar_dados

class TestLimparDados:
    def test_mes_ano_e_period(self, df_limpo):
        assert str(df_limpo["mes_ano"].dtype) == "period[M]"

    def test_campos_texto_maiusculos(self, df_limpo):
        for col in ["munic", "regiao"]:
            assert (df_limpo[col] == df_limpo[col].str.upper()).all(), f"{col} contém letras minúsculas"

    def test_melt_cria_colunas_esperadas(self, df_limpo):
        assert "tipo_crime" in df_limpo.columns
        assert "qtd_ocorrencias" in df_limpo.columns

    def test_tipo_crime_valores_validos(self, df_limpo):
        assert set(df_limpo["tipo_crime"].unique()).issubset(set(COLUNAS_VIOLENCIA))

    def test_sem_duplicatas(self, df_limpo):
        duplicatas = df_limpo.duplicated(subset=["cisp", "mes_ano", "tipo_crime"])
        assert not duplicatas.any()

    def test_qtd_ocorrencias_inteiro_nao_negativo(self, df_limpo):
        assert pd.api.types.is_integer_dtype(df_limpo["qtd_ocorrencias"])
        assert (df_limpo["qtd_ocorrencias"] >= 0).all()

    def test_nao_modifica_original(self, df_bruto):
        colunas_antes = list(df_bruto.columns)
        limpar_dados(df_bruto)
        assert list(df_bruto.columns) == colunas_antes


# gerar_metricas

class TestGerarMetricas:
    def test_colunas_de_metricas_criadas(self, df_metricas):
        for col in ["taxa_100k", "media_movel_3", "variacao_pct"]:
            assert col in df_metricas.columns, f"métrica ausente: {col}"

    def test_taxa_100k_nao_negativa(self, df_metricas):
        validos = df_metricas["taxa_100k"].dropna()
        assert (validos >= 0).all()

    def test_media_movel_nao_negativa(self, df_metricas):
        assert (df_metricas["media_movel_3"] >= 0).all()

    def test_aisp_sem_populacao_gera_taxa_nula(self, df_limpo):
        df_sem_pop = df_limpo.copy()
        df_sem_pop["aisp"] = "999"
        resultado = gerar_metricas(df_sem_pop)
        assert resultado["taxa_100k"].isna().all()

    def test_nao_modifica_original(self, df_limpo):
        colunas_antes = list(df_limpo.columns)
        gerar_metricas(df_limpo)
        assert list(df_limpo.columns) == colunas_antes


# analise_temporal

class TestAnaliseTemporal:
    def test_retorna_dataframe_com_colunas_esperadas(self, df_metricas):
        serie = analise_temporal(df_metricas)
        for col in ["total_ocorrencias", "taxa_100k_media", "media_movel_3"]:
            assert col in serie.columns

    def test_index_e_period(self, df_metricas):
        serie = analise_temporal(df_metricas)
        assert str(serie.index.dtype) == "period[M]"

    def test_filtro_tipo_crime(self, df_metricas):
        serie = analise_temporal(df_metricas, tipo_crime="hom_doloso")
        assert len(serie) > 0

    def test_filtro_aisp(self, df_metricas):
        serie_filtrada = analise_temporal(df_metricas, aisp="1")
        serie_total = analise_temporal(df_metricas)
        assert serie_filtrada["total_ocorrencias"].sum() <= serie_total["total_ocorrencias"].sum()

    def test_filtro_inexistente_retorna_vazio(self, df_metricas):
        serie = analise_temporal(df_metricas, tipo_crime="crime_inexistente")
        assert len(serie) == 0


# prever_tendencia

class TestPreverTendencia:
    @pytest.fixture
    def serie(self, df_metricas):
        return analise_temporal(df_metricas)

    def test_colunas_de_previsao_presentes(self, serie):
        resultado = prever_tendencia(serie, meses_futuros=3)
        for col in ["previsao", "intervalo_inf", "intervalo_sup"]:
            assert col in resultado.columns

    def test_numero_de_linhas_correto(self, serie):
        n_original = len(serie)
        resultado = prever_tendencia(serie, meses_futuros=3)
        assert len(resultado) == n_original + 3

    def test_previsao_nao_negativa(self, serie):
        resultado = prever_tendencia(serie, meses_futuros=3)
        futuros = resultado[resultado["previsao"].notna()]
        assert (futuros["previsao"] >= 0).all()

    def test_intervalo_inf_menor_que_sup(self, serie):
        resultado = prever_tendencia(serie, meses_futuros=3)
        futuros = resultado[resultado["previsao"].notna()]
        assert (futuros["intervalo_inf"] <= futuros["intervalo_sup"]).all()

    def test_periodos_futuros_apos_ultimo_mes(self, serie):
        ultimo_mes = serie.index.max()
        resultado = prever_tendencia(serie, meses_futuros=2)
        futuros = resultado[resultado["previsao"].notna()].index
        assert all(p > ultimo_mes for p in futuros)
