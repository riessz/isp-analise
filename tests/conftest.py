import pytest
from pipeline import carregar_dados, limpar_dados, gerar_metricas


_CSV_CONTEUDO = (
    "cisp;mes_ano;aisp;risp;munic;regiao;"
    "hom_doloso;latrocinio;cvli;letalidade_violenta\n"
    "1;2023m01;1;1;Rio de Janeiro;Capital;5;1;6;7\n"
    "1;2023m02;1;1;Rio de Janeiro;Capital;3;0;3;4\n"
    "1;2023m03;1;1;Rio de Janeiro;Capital;4;1;5;6\n"
    "1;2023m04;1;1;Rio de Janeiro;Capital;2;0;2;3\n"
    "2;2023m01;2;1;Niteroi;Metropolitana;2;0;2;3\n"
    "2;2023m02;2;1;Niteroi;Metropolitana;1;1;2;2\n"
    "2;2023m03;2;1;Niteroi;Metropolitana;3;0;3;4\n"
    "2;2023m04;2;1;Niteroi;Metropolitana;2;1;3;3\n"
)


# Fixtures: criam dados para ser usados nos testes, sem precisar repetir o código de criação em cada um.

@pytest.fixture
def csv_valido(tmp_path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_bytes(_CSV_CONTEUDO.encode("latin-1"))
    return arquivo


@pytest.fixture
def csv_colunas_faltando(tmp_path):
    conteudo = "cisp;mes_ano;aisp\n1;2023m01;1\n"
    arquivo = tmp_path / "incompleto.csv"
    arquivo.write_bytes(conteudo.encode("latin-1"))
    return arquivo


@pytest.fixture
def df_bruto(csv_valido):
    return carregar_dados(csv_valido)


@pytest.fixture
def df_limpo(df_bruto):
    return limpar_dados(df_bruto)


@pytest.fixture
def df_metricas(df_limpo):
    return gerar_metricas(df_limpo)
