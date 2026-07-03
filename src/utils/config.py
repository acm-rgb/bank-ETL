"""
Módulo de Configuração do Pipeline.
Centraliza todas as configurações lidas do arquivo .env.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Classe que carrega e valida as configurações do projeto."""
    
    # Configurações da API
    api_base_url: str = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"
    
     # Período de extração
    data_inicial: str = "01/01/2024"
    data_final: str = "31/12/2024"
    
    # Configurações de dados
    data_dir: Path = Path("./data")
    raw_data_dir: Path = Path("./data/raw")
    processed_data_dir: Path = Path("./data/processed")
    
    # Configurações de logging
    log_level: str = "INFO"
    
    # Configuração para ler do arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Instância global das configurações
settings = Settings()