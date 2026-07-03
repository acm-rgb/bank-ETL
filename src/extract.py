"""
Módulo de Extração do Pipeline.
Responsável por consumir a API do Banco Central e salvar os dados brutos.
"""
import json
from datetime import datetime
from pathlib import Path

import requests

from src.utils.config import settings
from src.utils.logger import logger


def build_url() -> str:
    """
    Constrói a URL completa da API com os parâmetros de data.
    
    Returns:
        URL completa com query string
    """
    params = {
        "formato": "json",
        "dataInicial": settings.data_inicial,
        "dataFinal": settings.data_final
    }
    
    # Constrói a URL com os parâmetros
    url = f"{settings.api_base_url}?formato={params['formato']}&dataInicial={params['dataInicial']}&dataFinal={params['dataFinal']}"
    
    logger.debug(f"URL construída: {url}")
    return url


def fetch_data(url: str) -> list[dict]:
    """
    Faz a requisição HTTP para a API e retorna os dados.
    
    Args:
        url: URL completa da API
        
    Returns:
        Lista de dicionários com os dados da API
        
    Raises:
        requests.exceptions.RequestException: Se houver erro na requisição
        ValueError: Se a resposta não for um JSON válido
    """
    logger.info(f"Iniciando requisição para a API...")
    
    try:
        # Timeout de 30 segundos para evitar que o script fique travado
        response = requests.get(url, timeout=30)
        
        # Verifica se o status code indica sucesso (200-299)
        response.raise_for_status()
        
        # Tenta converter para JSON
        data = response.json()
        
        # Valida se o retorno é uma lista
        if not isinstance(data, list):
            raise ValueError(f"Resposta inesperada da API. Esperado lista, recebido: {type(data)}")
        
        logger.info(f"Requisição bem-sucedida. {len(data)} registros obtidos.")
        return data
        
    except requests.exceptions.Timeout:
        logger.error("Timeout na requisição. A API demorou mais de 30 segundos para responder.")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP na requisição: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Resposta não é um JSON válido: {e}")
        raise ValueError("Resposta da API não é um JSON válido")


def save_raw_data(data: list[dict]) -> Path:
    """
    Salva os dados brutos em formato JSON na pasta data/raw/.
    
    Args:
        data: Lista de dicionários com os dados
        
    Returns:
        Caminho do arquivo salvo
    """
    # Garante que o diretório existe
    raw_dir = settings.raw_data_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dolar_{settings.data_inicial.replace('/', '')}_{settings.data_final.replace('/', '')}_{timestamp}.json"
    filepath = raw_dir / filename
    
    # Salva os dados
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Dados brutos salvos em: {filepath}")
    return filepath


def extract_data() -> Path:
    """
    Função principal de extração. Orquestra todo o processo.
    
    Returns:
        Caminho do arquivo JSON salvo
    """
    logger.info("=" * 60)
    logger.info("INICIANDO EXTRAÇÃO DE DADOS")
    logger.info("=" * 60)
    
    # Passo 1: Construir URL
    url = build_url()
    
    # Passo 2: Buscar dados
    data = fetch_data(url)
    
    # Passo 3: Validar se há dados
    if not data:
        logger.warning("Nenhum dado retornado pela API para o período especificado.")
        raise ValueError("Nenhum dado retornado pela API")
    
    # Passo 4: Salvar dados
    filepath = save_raw_data(data)
    
    logger.info("EXTRAÇÃO CONCLUÍDA COM SUCESSO")
    logger.info("=" * 60)
    
    return filepath


if __name__ == "__main__":
    # Permite testar o módulo isoladamente
    extract_data()