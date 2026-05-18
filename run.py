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

def main(caminho_csv: str | Path) -> None:
    log.info("=== Iniciando pipeline ===")

    try:
        df_bruto    = carregar_dados(caminho_csv)
        df_limpo    = limpar_dados(df_bruto)
        df_metricas = gerar_metricas(df_limpo)

    except (FileNotFoundError, ValueError) as e:
        log.error("Pipeline interrompido: %s", e)
        raise

    except Exception as e:
        log.exception("Erro inesperado no pipeline: %s", e)
        raise

    _salvar_processados(df_limpo, df_metricas)
    log.info("=== Pipeline concluído com sucesso ===")


def _salvar_processados(df_limpo: pd.DataFrame, df_metricas: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_limpo.to_csv(PROCESSED_DIR / "dados_limpos.csv", index=False)
    df_metricas.to_csv(PROCESSED_DIR / "dados_metricas.csv", index=False)
    log.info("Dados salvos em %s", PROCESSED_DIR)



# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else ARQUIVO_PADRAO
    main(caminho)
