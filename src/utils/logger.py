"""
Módulo de Logging do Pipeline.
Configura um logger padronizado para todo o projeto.
"""
import logging
import sys
from .config import settings


def setup_logger(name: str = "bank_etl") -> logging.Logger:
    """
    Configura e retorna um logger padronizado.
    
    Args:
        name: Nome do logger (geralmente o nome do módulo)
    
    Returns:
        Logger configurado
    """
    # Cria o logger
    logger = logging.getLogger(name)
    
    # Define o nível de log baseado na configuração
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Evita duplicação de handlers se o logger já foi configurado
    if logger.handlers:
        return logger
    
    # Formato da mensagem de log
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (opcional, mas recomendado para produção)
    # file_handler = logging.FileHandler("pipeline.log", encoding="utf-8")
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    
    return logger


# Logger global que pode ser importado em outros módulos
logger = setup_logger()