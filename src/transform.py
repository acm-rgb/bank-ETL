"""
Módulo de Transformação do Pipeline.
Responsável por limpar, transformar e enriquecer os dados brutos.
"""
from pathlib import Path
from datetime import datetime

import polars as pl

from src.utils.config import settings
from src.utils.logger import logger


def load_raw_data(filepath: Path) -> pl.DataFrame:
    """
    Carrega os dados brutos do arquivo JSON.
    
    Args:
        filepath: Caminho do arquivo JSON
        
    Returns:
        DataFrame do Polars com os dados brutos
    """
    logger.info(f"Carregando dados brutos de: {filepath}")
    
    if not filepath.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    # Polars lê JSON diretamente
    df = pl.read_json(filepath)
    
    logger.info(f"Dados carregados: {df.shape[0]} linhas, {df.shape[1]} colunas")
    return df


def clean_and_type_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Limpa os dados e converte os tipos.
    
    Args:
        df: DataFrame com dados brutos
        
    Returns:
        DataFrame com tipos corrigidos
    """
    logger.info("Limpando e tipando os dados...")
    
    # Renomeia colunas para seguir convenção snake_case
    df = df.rename({
        "data": "data",
        "valor": "valor"
    })
    
    # Converte data de string para datetime
    # Formato da API: dd/mm/yyyy
    df = df.with_columns(
        pl.col("data").str.to_datetime("%d/%m/%Y").alias("data")
    )
    
    # Converte valor de string para float
    # Remove vírgulas e converte para float (se houver)
    df = df.with_columns(
        pl.col("valor").str.replace(",", ".").cast(pl.Float64).alias("valor")
    )
    
    # Remove linhas nulas
    df = df.drop_nulls()
    
    logger.info(f"Dados após limpeza: {df.shape[0]} linhas, {df.shape[1]} colunas")
    return df


def enrich_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Enriquece os dados com colunas derivadas.
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        DataFrame com colunas adicionais
    """
    logger.info("Enriquecendo dados com colunas derivadas...")
    
    df = df.with_columns([
        # Extrai componentes da data
        pl.col("data").dt.year().alias("ano"),
        pl.col("data").dt.month().alias("mes"),
        pl.col("data").dt.day().alias("dia"),
        pl.col("data").dt.weekday().alias("dia_semana"),  # 1=segunda, 7=domingo
        
        # Calcula variação diária (percentual)
        pl.col("valor").pct_change().alias("variacao_diaria"),
        
        # Calcula média móvel de 7 dias
        pl.col("valor").rolling_mean(window_size=7).alias("media_movel_7d"),
    ])
    
    logger.info(f"Dados após enriquecimento: {df.shape[0]} linhas, {df.shape[1]} colunas")
    return df


def sort_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ordena os dados por data.
    
    Args:
        df: DataFrame com dados
        
    Returns:
        DataFrame ordenado
    """
    logger.info("Ordenando dados por data...")
    df = df.sort("data")
    return df


def save_processed_data(df: pl.DataFrame) -> Path:
    """
    Salva os dados processados em formato Parquet.
    
    Args:
        df: DataFrame processado
        
    Returns:
        Caminho do arquivo Parquet salvo
    """
    # Garante que o diretório existe
    processed_dir = settings.processed_data_dir
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dolar_processed_{timestamp}.parquet"
    filepath = processed_dir / filename
    
    # Salva em Parquet com compressão snappy (padrão da indústria)
    df.write_parquet(filepath, compression="snappy")
    
    logger.info(f"Dados processados salvos em: {filepath}")
    return filepath


def transform_data(raw_filepath: Path) -> Path:
    """
    Função principal de transformação. Orquestra todo o processo.
    
    Args:
        raw_filepath: Caminho do arquivo JSON bruto
        
    Returns:
        Caminho do arquivo Parquet salvo
    """
    logger.info("=" * 60)
    logger.info("INICIANDO TRANSFORMAÇÃO DE DADOS")
    logger.info("=" * 60)
    
    # Passo 1: Carregar dados
    df = load_raw_data(raw_filepath)
    
    # Passo 2: Limpar e tipar
    df = clean_and_type_data(df)
    
    # Passo 3: Enriquecer
    df = enrich_data(df)
    
    # Passo 4: Ordenar
    df = sort_data(df)
    
    # Passo 5: Salvar
    filepath = save_processed_data(df)
    
    logger.info("TRANSFORMAÇÃO CONCLUÍDA COM SUCESSO")
    logger.info("=" * 60)
    
    return filepath


if __name__ == "__main__":
    # Permite testar o módulo isoladamente
    # Encontra o arquivo JSON mais recente na pasta raw
    raw_dir = settings.raw_data_dir
    json_files = list(raw_dir.glob("*.json"))
    
    if not json_files:
        logger.error("Nenhum arquivo JSON encontrado na pasta data/raw/")
        raise FileNotFoundError("Nenhum arquivo JSON encontrado")
    
    # Pega o arquivo mais recente
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Usando arquivo mais recente: {latest_file}")
    
    transform_data(latest_file)