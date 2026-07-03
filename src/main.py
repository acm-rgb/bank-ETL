"""
Módulo Orquestrador do Pipeline.
Coordena a execução das etapas Extract, Transform e Load.
"""
from pathlib import Path
from datetime import datetime

from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data
from src.utils.logger import logger
from src.utils.config import settings


def run_pipeline() -> None:
    """
    Executa o pipeline ETL completo.
    
    Fluxo:
    1. Extract: Baixa dados da API e salva em JSON
    2. Transform: Limpa, enriquece e salva em Parquet
    3. Load: Carrega dados no DuckDB
    """
    start_time = datetime.now()
    
    logger.info("=" * 80)
    logger.info("INICIANDO PIPELINE ETL COMPLETO")
    logger.info(f"Timestamp: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    try:
        # ETAPA 1: EXTRAÇÃO
        logger.info("\n" + "=" * 80)
        logger.info("ETAPA 1/3: EXTRAÇÃO")
        logger.info("=" * 80)
        
        raw_filepath = extract_data()
        
        if not raw_filepath.exists():
            raise FileNotFoundError(f"Arquivo bruto não foi criado: {raw_filepath}")
        
        logger.info(f"✓ Extração concluída: {raw_filepath}")
        
        # ETAPA 2: TRANSFORMAÇÃO
        logger.info("\n" + "=" * 80)
        logger.info("ETAPA 2/3: TRANSFORMAÇÃO")
        logger.info("=" * 80)
        
        processed_filepath = transform_data(raw_filepath)
        
        if not processed_filepath.exists():
            raise FileNotFoundError(f"Arquivo processado não foi criado: {processed_filepath}")
        
        logger.info(f"✓ Transformação concluída: {processed_filepath}")
        
        # ETAPA 3: CARGA
        logger.info("\n" + "=" * 80)
        logger.info("ETAPA 3/3: CARGA")
        logger.info("=" * 80)
        
        db_filepath = load_data(processed_filepath)
        
        if not db_filepath.exists():
            raise FileNotFoundError(f"Banco de dados não foi criado: {db_filepath}")
        
        logger.info(f"✓ Carga concluída: {db_filepath}")
        
        # SUCESSO
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
        logger.info(f"Duração total: {duration:.2f} segundos")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n{'=' * 80}")
        logger.error("ERRO NO PIPELINE")
        logger.error(f"{'=' * 80}")
        logger.error(f"Tipo de erro: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"{'=' * 80}")
        raise


if __name__ == "__main__":
    run_pipeline()