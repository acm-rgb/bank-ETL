"""Script para inspecionar o arquivo Parquet gerado."""
import polars as pl
from src.utils.config import settings

# Encontra o arquivo Parquet mais recente
processed_dir = settings.processed_data_dir
parquet_files = list(processed_dir.glob("*.parquet"))
latest_file = max(parquet_files, key=lambda p: p.stat().st_mtime)

print(f"Arquivo: {latest_file}")
print(f"Tamanho: {latest_file.stat().st_size / 1024:.2f} KB")
print()

# Lê e mostra os dados
df = pl.read_parquet(latest_file)
print(f"Shape: {df.shape}")
print()
print("Primeiras 10 linhas:")
print(df.head(10))
print()
print("Estatísticas:")
print(df.describe())