"""
Aplicativo Streamlit para visualização dos dados macroeconômicos.
"""
import duckdb
import polars as pl
import streamlit as st
from pathlib import Path
from datetime import datetime

# Configuração da página (deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Dashboard Macroeconômico",
    page_icon="📊",
    layout="wide"
)

# Caminho do banco de dados
DB_PATH = Path("./data/processed/macro_data.db")


@st.cache_resource
def get_database_connection() -> duckdb.DuckDBPyConnection:
    """
    Cria conexão com o banco DuckDB (cacheada pelo Streamlit).
    
    Returns:
        Conexão DuckDB
    """
    if not DB_PATH.exists():
        st.error(f"Banco de dados não encontrado: {DB_PATH}")
        st.info("Execute o pipeline primeiro: `python -m src.main`")
        st.stop()
    
    return duckdb.connect(str(DB_PATH))


@st.cache_data
def load_data(_conn: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """
    Carrega todos os dados do banco.
    
    Args:
        _conn: Conexão DuckDB (o underscore indica que não deve ser cacheado)
        
    Returns:
        DataFrame Polars com todos os dados
    """
    # Busca como DataFrame Pandas
    df_pandas = _conn.execute("SELECT * FROM dolar_historico ORDER BY data").fetchdf()
    
    # Converte para Polars
    df = pl.from_pandas(df_pandas)
    
    return df


def main():
    """Função principal do aplicativo."""
    
    # Título
    st.title("📊 Dashboard Macroeconômico")
    st.markdown("---")
    
    # Conecta ao banco
    conn = get_database_connection()
    
    # Carrega dados
    df = load_data(conn)
    
    if df.is_empty():
        st.warning("Nenhum dado disponível. Execute o pipeline primeiro.")
        st.stop()
    
    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de período
    min_date = df["data"].min().date()
    max_date = df["data"].max().date()
    
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Aplica filtro de data
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df.filter(
            (pl.col("data").dt.date() >= start_date) & 
            (pl.col("data").dt.date() <= end_date)
        )
    else:
        df_filtered = df
    
    # Métricas principais
    st.subheader("📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        valor_atual = df_filtered["valor"][-1]
        st.metric(
            label="Cotação Atual",
            value=f"R$ {valor_atual:.4f}",
            delta=None
        )
    
    with col2:
        valor_medio = df_filtered["valor"].mean()
        st.metric(
            label="Média do Período",
            value=f"R$ {valor_medio:.4f}"
        )
    
    with col3:
        valor_min = df_filtered["valor"].min()
        st.metric(
            label="Mínimo do Período",
            value=f"R$ {valor_min:.4f}"
        )
    
    with col4:
        valor_max = df_filtered["valor"].max()
        st.metric(
            label="Máximo do Período",
            value=f"R$ {valor_max:.4f}"
        )
    
    st.markdown("---")
    
    # Gráfico de evolução
    st.subheader("📉 Evolução da Cotação")
    
    chart_data = df_filtered.select(["data", "valor"]).to_pandas()
    chart_data = chart_data.set_index("data")
    
    st.line_chart(chart_data["valor"])
    
    st.markdown("---")
    
    # Estatísticas detalhadas
    st.subheader("📊 Estatísticas Detalhadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Por Mês")
        
        monthly_stats = df_filtered.group_by(["ano", "mes"]).agg([
            pl.col("valor").mean().alias("media"),
            pl.col("valor").min().alias("minimo"),
            pl.col("valor").max().alias("maximo"),
        ]).sort(["ano", "mes"])
        
        st.dataframe(
            monthly_stats.to_pandas(),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("#### Maiores Variações")
        
        top_variations = df_filtered.filter(
            pl.col("variacao_diaria").is_not_null()
        ).sort("variacao_diaria", descending=True).head(10)
        
        top_variations = top_variations.select([
            "data",
            "valor",
            (pl.col("variacao_diaria") * 100).alias("variacao_pct")
        ])
        
        st.dataframe(
            top_variations.to_pandas(),
            use_container_width=True,
            hide_index=True,
            column_config={
                "variacao_pct": st.column_config.NumberColumn(
                    "Variação (%)",
                    format="%.2f%%"
                )
            }
        )
    
    st.markdown("---")
    
    # Dados brutos
    with st.expander("📋 Ver Dados Completos"):
        st.dataframe(
            df_filtered.to_pandas(),
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"*Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*"
    )


if __name__ == "__main__":
    main()