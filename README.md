# Inteligência Territorial e Segurança Pública — Rio de Janeiro

![CI](https://github.com/riessz/isp-analise/actions/workflows/ci.yml/badge.svg)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://publicsecurityrj.streamlit.app/)

Análise de dados de criminalidade do estado do Rio de Janeiro a partir dos registros mensais por CISP (Circunscrição de Segurança Pública) disponibilizados pelo ISP-RJ.

## Fonte de dados

[ISP-RJ — Instituto de Segurança Pública](https://www.ispdados.rj.gov.br)  
Arquivo: `BaseDPEvolucaoMensalCisp.csv`

## Estrutura do projeto

```
isp-analise/
├── data/
│   ├── raw/                        # CSV bruto do ISP-RJ
│   └── processed/                  # Saídas do pipeline (geradas por run.py)
│       ├── dados_limpos.csv
│       └── dados_metricas.csv
├── notebooks/
│   ├── 01_carregar.ipynb
│   ├── 02_limpeza.ipynb
│   ├── 03_metricas.ipynb
│   ├── 04_temporal.ipynb
│   ├── 05_visualizacao.ipynb
│   └── 06_previsao.ipynb
├── tests/
│   ├── conftest.py
│   └── test_pipeline.py
├── app.py                          # Dashboard interativo (Streamlit)
├── pipeline.py                     # Funções do pipeline
├── run.py                          # Orquestrador / entry point CLI
└── requirements.txt
```

## Pipeline

```
CSV bruto
  → carregar_dados()        # leitura e validação de colunas
  → limpar_dados()          # normalização, parsing de datas, melt para formato longo
  → gerar_metricas()        # taxa por 100k hab., média móvel 3 meses, variação %
  → analise_temporal()      # série temporal agregada por crime/AISP
  → prever_tendencia()      # regressão linear com intervalo de confiança
```

## Grupos de crimes analisados

| Grupo     | Variáveis                                                            |
|-----------|----------------------------------------------------------------------|
| Violência | `hom_doloso`, `latrocinio`, `cvli`, `letalidade_violenta`           |
| Roubo     | `roubo_veiculo`, `roubo_celular`, `roubo_transeunte`, `total_roubos`|
| Drogas    | `posse_drogas`, `trafico_drogas`                                     |
| Furto     | `furto_celular`, `furto_transeunte`                                  |

> **Atenção:** `total_roubos` inclui modalidades além das três listadas (roubo a banco, carga etc.). Combiná-lo com os tipos individuais gera dupla contagem, o dashboard exibe um aviso automático nesse caso.

## Instalação

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Uso

**Demo online:** [publicsecurityrj.streamlit.app](https://publicsecurityrj.streamlit.app/)

**Dashboard interativo (Streamlit, local):**

```bash
streamlit run app.py
```

Filtros disponíveis na sidebar: período (por ano), AISP, grupo de crime e tipo de crime.  
Cada AISP tem sua região descrita em um expander — sem precisar pesquisar externamente.

**Executar o pipeline via linha de comando:**

```bash
python run.py
# ou com caminho customizado
python run.py caminho/para/arquivo.csv
```

Gera `data/processed/dados_limpos.csv` e `data/processed/dados_metricas.csv`.

**Usar as funções individualmente:**

```python
from pipeline import (
    carregar_dados, limpar_dados, gerar_metricas,
    COLUNAS_VIOLENCIA, COLUNAS_ROUBO, COLUNAS_DROGAS, COLUNAS_FURTO, COLUNAS_CRIME,
)

df = carregar_dados("data/raw/BaseDPEvolucaoMensalCisp.csv")
df = limpar_dados(df, colunas_crime=COLUNAS_CRIME)  # todos os grupos
df = gerar_metricas(df)
```

**Explorar pelos notebooks** (ordem recomendada: `01` → `06`):

```bash
jupyter notebook
```

## Testes

```bash
pytest tests/ -v
```

27 testes cobrindo todas as funções do pipeline (`carregar_dados`, `limpar_dados`, `gerar_metricas`, `analise_temporal`, `prever_tendencia`).

## Requisitos

- Python 3.10+
- pandas, numpy, scikit-learn, scipy, streamlit, plotly (ver `requirements.txt`)

## Autor

Arthur Riess Cunha
