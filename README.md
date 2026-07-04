# 📊 Bank ETL - Pipeline de Indicadores Macroeconômicos

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Polars](https://img.shields.io/badge/Polars-0.20%2B-orange)](https://pola.rs/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.10%2B-yellow)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)](https://www.docker.com/)

Pipeline ETL profissional que consome dados da API do Banco Central do Brasil, processa com Polars e disponibiliza via dashboard interativo Streamlit.

---

## 📋 Visão Geral

Este projeto demonstra competências em **Engenharia de Dados** através da construção de um pipeline completo que:

1. **Extrai** dados da API do Banco Central (cotação do Dólar)
2. **Transforma** com Polars (limpeza, tipagem, enriquecimento)
3. **Carrega** em DuckDB (banco analítico local)
4. **Serve** via dashboard Streamlit interativo
5. **Dockeriza** tudo para deploy em qualquer ambiente

---

## 🏗️ Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  API BCB    │ ───> │   Extract    │ ───> │  Transform  │ ───> │     Load     │
│  (REST)     │      │   (JSON)     │      │   (Polars)  │      │   (DuckDB)   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                                        │
                                                                        ▼
                                                               ┌──────────────┐
                                                               │  Streamlit   │
                                                               │  Dashboard   │
                                                               └──────────────┘
```

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| Python | 3.10+ | Linguagem principal |
| Polars | 0.20+ | Manipulação de dados (10-100x mais rápido que Pandas) |
| DuckDB | 0.10+ | Banco de dados analítico local |
| Streamlit | 1.30+ | Dashboard interativo |
| Docker | Latest | Containerização |
| Pydantic | 2.0+ | Validação de configurações |
| Requests | 2.31+ | Consumo de API |

---

## 📁 Estrutura do Projeto

```
bank_ETL/
├── data/                       # Dados (ignorado pelo Git)
│   ├── raw/                    # Dados brutos (JSON)
│   └── processed/              # Dados processados (Parquet + DuckDB)
├── src/                        # Código do pipeline ETL
│   ├── extract.py              # Extração da API
│   ├── transform.py            # Transformação com Polars
│   ├── load.py                 # Carga no DuckDB
│   ├── main.py                 # Orquestrador
│   └── utils/                  # Módulos auxiliares
│       ├── config.py           # Configurações (.env)
│       └── logger.py           # Logging profissional
├── streamlit_app/              # Dashboard
│   └── app.py                  # Aplicação Streamlit
├── tests/                      # Testes unitários
├── .env                        # Variáveis de ambiente
├── .gitignore                  # Ignorados pelo Git
├── pyproject.toml              # Dependências e configuração
├── Dockerfile.pipeline         # Docker do pipeline
├── Dockerfile.streamlit        # Docker do dashboard
└── docker-compose.yml          # Orquestração Docker
```

---

## 🚀 Como Executar

### Opção 1: Local (com Python)

#### Pré-requisitos
- Python 3.10+
- pip

#### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/bank_ETL.git
cd bank_ETL

# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install -e .
```

#### Executando o Pipeline

```bash
# Executa Extract → Transform → Load
python -m src.main
```

#### Executando o Dashboard

```bash
streamlit run streamlit_app/app.py
```

Acesse: http://localhost:8501

---

### Opção 2: Docker (Recomendado)

#### Pré-requisitos
- Docker Desktop
- Docker Compose

#### Executando

```bash
# 1. Construa as imagens
docker-compose build

# 2. Execute o pipeline (gera os dados)
docker-compose run --rm pipeline

# 3. Inicie o dashboard
docker-compose up streamlit
```

Acesse: http://localhost:8501

#### Parando os containers

```bash
# Pare com Ctrl+C, depois:
docker-compose down
```

---

## 📊 Dashboard

O dashboard Streamlit oferece:

- 📈 **Métricas principais**: Cotação atual, média, mínimo e máximo
- 📉 **Gráfico de evolução**: Visualização temporal da cotação
- 📊 **Estatísticas mensais**: Agregações por mês
- 🔄 **Maiores variações**: Top 10 dias com maior variação percentual
- 🔍 **Filtros interativos**: Selecione período personalizado

## 🔄 Fluxo de Dados

1. **Extract**: Consome API do BCB → salva JSON em `data/raw/`
2. **Transform**: Lê JSON → limpa, tipa, enriquece → salva Parquet em `data/processed/`
3. **Load**: Lê Parquet → carrega no DuckDB → cria índices
4. **Serve**: Streamlit lê DuckDB → exibe dashboard interativo

---

## 📚 Aprendizados

Este projeto demonstra:

✅ **Arquitetura profissional** com separação de responsabilidades  
✅ **Logging estruturado** para debug e monitoramento  
✅ **Configuração externa** via `.env` com validação  
✅ **Transformações eficientes** com Polars (Rust-based)  
✅ **Formato analítico** Parquet (padrão da indústria)  
✅ **Banco colunar** DuckDB para queries otimizadas  
✅ **Containerização** com Docker para portabilidade  

---

## 🚧 Próximos Passos

- [ ] Adicionar testes unitários com pytest
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Agendar execução automática (cron/Airflow)
- [ ] Deploy do Streamlit na nuvem (Streamlit Cloud)
- [ ] Adicionar mais séries temporais (IPCA, Selic, PIB)

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

---

## 📧 Contato

**André** - [LinkedIn](https://linkedin.com/in/andrecamposmoreira) - andrecm.pessoal@gmail.com

Projeto: [https://github.com/seu-usuario/bank_ETL](https://github.com/seu-usuario/bank_ETL)

---

<div align="center">

**Feito com ❤️ por André**

</div>