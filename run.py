from pathlib import Path
import logging
import sys

import pandas as pd

from pipeline import (
    ARQUIVO_PADRAO,
    PROCESSED_DIR,
    carregar_dados,
    limpar_dados,
    gerar_metricas,
    preparar_visualizacao,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# =============================================================================
# ORQUESTRADOR
# =============================================================================

def main(caminho_csv: str | Path) -> dict[str, pd.DataFrame]:
    log.info("=== Iniciando pipeline ===")

    try:
        df_bruto    = carregar_dados(caminho_csv)
        df_limpo    = limpar_dados(df_bruto)
        df_metricas = gerar_metricas(df_limpo)
        resultado   = preparar_visualizacao(df_metricas)

    except (FileNotFoundError, ValueError) as e:
        log.error("Pipeline interrompido: %s", e)
        raise

    except Exception as e:
        log.exception("Erro inesperado no pipeline: %s", e)
        raise

    _salvar_processados(df_limpo, df_metricas)
    log.info("=== Pipeline concluído com sucesso ===")
    return resultado


def _salvar_processados(df_limpo: pd.DataFrame, df_metricas: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_limpo.to_csv(PROCESSED_DIR / "dados_limpos.csv", index=False)
    df_metricas.to_csv(PROCESSED_DIR / "dados_metricas.csv", index=False)
    log.info("Dados salvos em %s", PROCESSED_DIR)


def _inspecionar(dados: dict[str, pd.DataFrame]) -> None:
    series   = dados["series"]
    ranking  = dados["ranking"]
    por_tipo = dados["por_tipo"]
    heatmap  = dados["heatmap"]

    periodo_ini = series.index.min()
    periodo_fim = series.index.max()
    total       = int(series["total_ocorrencias"].sum())

    print("\n" + "=" * 52)
    print("  RESUMO DO PIPELINE")
    print("=" * 52)
    print(f"  Periodo      : {periodo_ini} a {periodo_fim}")
    print(f"  Total crimes : {total:,}")
    print(f"  AISPs        : {heatmap.shape[0]}")
    print(f"  Meses        : {heatmap.shape[1]}")

    print("\n--- Top 5 AISPs (mês mais recente) ---")
    print(ranking.head(5).to_string(index=False))

    print("\n--- Distribuição por tipo de crime ---")
    print(por_tipo.to_string(index=False))

    print("\n--- Série temporal (últimos 6 meses) ---")
    print(series.tail(6).to_string())
    print("=" * 52)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else ARQUIVO_PADRAO
    dados = main(caminho)
    _inspecionar(dados)
