# Inteligência Territorial e Segurança Pública — Rio de Janeiro

Análise de dados de criminalidade do estado do Rio de Janeiro a partir dos registros mensais por CISP (Circunscrição de Segurança Pública) disponibilizados pelo ISP-RJ.

## Fonte de dados

[ISP-RJ — Instituto de Segurança Pública](https://www.ispdados.rj.gov.br)  
Arquivo: `BaseDPEvolucaoMensalCisp.csv`

## Estrutura do projeto

```
isp-analise/
├── data/
│   └── raw/                        # CSV bruto do ISP-RJ
├── notebooks/
│   ├── 01_carregar.ipynb
│   ├── 02_limpeza.ipynb
│   ├── 03_metricas.ipynb
│   ├── 04_temporal.ipynb
│   ├── 05_visualizacao.ipynb
│   └── 06_previsao.ipynb
├── pipeline.py                     # Funções do pipeline
├── run.py                          # Orquestrador / entry point
└── requirements.txt
```

## Pipeline

```
CSV bruto
  → carregar_dados()       # leitura e validação de colunas
  → limpar_dados()         # normalização, parsing de datas, melt para formato longo
  → gerar_metricas()       # taxa por 100k hab., média móvel 3 meses, variação %
  → analise_temporal()     # série temporal agregada por crime/AISP
  → preparar_visualizacao()# heatmap, ranking, série, distribuição por tipo
  → [futuro] prever_tendencia()  # regressão linear com intervalo de confiança
```

## Grupos de crimes analisados

| Grupo      | Variáveis                                                       |
|------------|----------------------------------------------------------------|
| Violência  | `hom_doloso`, `latrocinio`, `cvli`, `letalidade_violenta`      |
| Roubos     | `roubo_veiculo`, `roubo_celular`, `roubo_transeunte`, `total_roubos` |
| Drogas     | `posse_drogas`, `trafico_drogas`                               |

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

**Executar o pipeline completo via linha de comando:**

```bash
python run.py
# ou com caminho customizado
python run.py caminho/para/arquivo.csv
```

**Usar as funções individualmente:**

```python
from pipeline import carregar_dados, limpar_dados, gerar_metricas, preparar_visualizacao

df = carregar_dados("data/raw/BaseDPEvolucaoMensalCisp.csv")
df = limpar_dados(df)
df = gerar_metricas(df)
dados = preparar_visualizacao(df)
# dados["heatmap"], dados["ranking"], dados["series"], dados["por_tipo"]
```

**Explorar pelos notebooks** (ordem recomendada: `01` → `06`):

```bash
jupyter notebook
```

## Requisitos

- Python 3.10+
- pandas, numpy, scikit-learn, scipy (ver `requirements.txt`)

## Autor

Arthur Riess Cunha
