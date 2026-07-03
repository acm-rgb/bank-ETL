"""
Módulo de Carga do Pipeline.
Responsável por carregar os dados processados no DuckDB.
"""
from pathlib import Path
from datetime import datetime

import duckdb
import polars as pl

from src.utils.config import settings
from src.utils.logger import logger


def create_database_connection(db_path: Path = None) -> duckdb.DuckDBPyConnection:
    """
    Cria uma conexão com o banco DuckDB.
    
    Args:
        db_path: Caminho do arquivo do banco (se None, usa o padrão)
        
    Returns:
        Conexão DuckDB
    """
    if db_path is None:
        db_path = settings.processed_data_dir / "macro_data.db"
    
    logger.info(f"Conectando ao banco DuckDB: {db_path}")
    
    # Cria o diretório se não existir
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Conecta ao banco (cria o arquivo se não existir)
    conn = duckdb.connect(str(db_path))
    
    logger.info("Conexão estabelecida com sucesso")
    return conn


def load_to_duckdb(parquet_path: Path, conn: duckdb.DuckDBPyConnection) -> None:
    """
    Carrega os dados do Parquet para o DuckDB.
    
    Args:
        parquet_path: Caminho do arquivo Parquet
        conn: Conexão DuckDB
    """
    logger.info(f"Carregando dados de: {parquet_path}")
    
    # Lê o Parquet
    df = pl.read_parquet(parquet_path)
    
    # Cria uma tabela no DuckDB (substitui se já existir)
    table_name = "dolar_historico"
    
    # Converte Polars DataFrame para DuckDB e cria a tabela
    # DuckDB pode ler diretamente de DataFrames do Polars
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    
    logger.info(f"Tabela '{table_name}' criada com {df.shape[0]} registros")


def create_indexes(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Cria índices para otimizar consultas.
    
    Args:
        conn: Conexão DuckDB
    """
    logger.info("Criando índices para otimização...")
    
    table_name = "dolar_historico"
    
    # Índice na coluna data (para filtros por período)
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_data ON {table_name} (data)")
    
    # Índice na coluna ano (para filtros por ano)
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_ano ON {table_name} (ano)")
    
    logger.info("Índices criados com sucesso")


def validate_load(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Valida se os dados foram carregados corretamente.
    
    Args:
        conn: Conexão DuckDB
    """
    logger.info("Validando carga de dados...")
    
    # Conta registros
    result = conn.execute("SELECT COUNT(*) as total FROM dolar_historico").fetchone()
    total = result[0]
    
    logger.info(f"Total de registros na tabela: {total}")
    
    # Mostra algumas estatísticas
    stats = conn.execute("""
        SELECT 
            MIN(data) as data_minima,
            MAX(data) as data_maxima,
            AVG(valor) as valor_medio,
            MIN(valor) as valor_minimo,
            MAX(valor) as valor_maximo
        FROM dolar_historico
    """).fetchone()
    
    logger.info(f"Período dos dados: {stats[0]} até {stats[1]}")
    logger.info(f"Estatísticas do valor: min={stats[3]:.4f}, max={stats[4]:.4f}, avg={stats[2]:.4f}")
    
    if total == 0:
        raise ValueError("Nenhum dado foi carregado na tabela")


def load_data(parquet_path: Path) -> Path:
    """
    Função principal de carga. Orquestra todo o processo.
    
    Args:
        parquet_path: Caminho do arquivo Parquet
        
    Returns:
        Caminho do banco de dados
    """
    logger.info("=" * 60)
    logger.info("INICIANDO CARGA DE DADOS")
    logger.info("=" * 60)
    
    # Passo 1: Conectar ao banco
    conn = create_database_connection()
    
    try:
        # Passo 2: Carregar dados
        load_to_duckdb(parquet_path, conn)
        
        # Passo 3: Criar índices
        create_indexes(conn)
        
        # Passo 4: Validar
        validate_load(conn)
        
        logger.info("CARGA CONCLUÍDA COM SUCESSO")
        logger.info("=" * 60)
        
        # Retorna o caminho do banco
        db_path = settings.processed_data_dir / "macro_data.db"
        return db_path
        
    finally:
        # Sempre fecha a conexão
        conn.close()
        logger.info("Conexão com o banco fechada")


if __name__ == "__main__":
    # Permite testar o módulo isoladamente
    # Encontra o arquivo Parquet mais recente na pasta processed
    processed_dir = settings.processed_data_dir
    parquet_files = list(processed_dir.glob("*.parquet"))
    
    if not parquet_files:
        logger.error("Nenhum arquivo Parquet encontrado na pasta data/processed/")
        raise FileNotFoundError("Nenhum arquivo Parquet encontrado")
    
    # Pega o arquivo mais recente
    latest_file = max(parquet_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Usando arquivo mais recente: {latest_file}")
    
    load_data(latest_file)