# Air Quality Pipeline 🌬️

Pipeline de dados end-to-end para monitoramento de qualidade do ar no Brasil, com foco em poluentes químicos (PM2.5, PM10, NO₂, O₃, CO, SO₂).

> **Status:** Em desenvolvimento ativo — Etapas 1 e 2 concluídas (ingestão + transformação raw)

---

## Visão geral

Este projeto constrói uma arquitetura moderna de dados que ingere medições de qualidade do ar de múltiplas fontes públicas, processa e transforma os dados em camadas (raw → silver → gold) e os disponibiliza para análise via Athena e dashboard.

A motivação é demonstrar o impacto da poluição atmosférica na saúde pública brasileira cruzando dados de poluentes com indicadores de internações hospitalares (DataSUS).

---

## Arquitetura

```
Fontes (OpenAQ API, INMET API)
        ↓
Ingestão (Python + PySpark)
        ↓
Data Lake S3  ── raw/ ── silver/ ── gold/
        ↓
Glue Catalog (metadados)
        ↓
Transformação (dbt + Athena)
        ↓
Dashboard (Looker Studio)  ←  Orquestração (Airflow)
```

### Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Ingestão | Python 3.11, boto3, requests |
| Data Lake | AWS S3 (raw / silver / gold) |
| Catálogo | AWS Glue Data Catalog |
| Transformação | dbt-athena-community 1.10 |
| Query engine | AWS Athena |
| Orquestração | Apache Airflow 2.8 (Docker) |
| Processamento | Apache Spark 3.4 (Docker) |
| Dashboard | Looker Studio (em construção) |
| Qualidade | Great Expectations (planejado) |

---

## Fontes de dados

| Fonte | Descrição | Cobertura |
|---|---|---|
| [OpenAQ v3](https://api.openaq.org) | Medições de poluentes por estação | 100+ estações BR |
| [INMET](https://apitempo.inmet.gov.br) | Dados meteorológicos automáticos | 679 estações BR |
| IEMA (planejado) | Histórico multi-estados | SP, RJ, MG, PE, RS |
| DataSUS (planejado) | Internações respiratórias | Nacional |

### Poluentes monitorados

`PM2.5` `PM10` `NO₂` `O₃` `CO` `SO₂` `NO` `NOx`

---

## Estrutura do projeto

```
air-quality-pipeline/
├── ingestion/
│   ├── extractors/
│   │   ├── openaq_extractor.py      # OpenAQ API v3
│   │   └── inmet_extractor.py       # INMET API
│   └── loaders/
│       └── create_glue_tables.py    # Registro no Glue Catalog
├── transformation/
│   └── air_quality/                 # Projeto dbt
│       └── models/
│           ├── raw/                 # Views de leitura bruta
│           │   ├── raw_openaq_stations.sql
│           │   └── raw_inmet_stations.sql
│           ├── silver/              # Em construção
│           └── gold/                # Em construção
├── orchestration/
│   └── dags/                        # DAGs Airflow (em construção)
├── tests/
├── docs/
├── docker-compose.yml               # Airflow + Spark + Postgres
├── requirements.txt
└── .env.example
```

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11+
- Docker Desktop
- AWS CLI configurado (`aws configure`)
- Conta AWS com permissões S3, Athena e Glue

### Setup

```bash
# Clone o repositório
git clone https://github.com/TayschreN/air-quality-pipeline.git
cd air-quality-pipeline

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Suba o ambiente Docker (Airflow + Spark)
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler spark postgres
```

### Ingestão manual

```bash
# Dados do OpenAQ (estações brasileiras)
python ingestion/extractors/openaq_extractor.py

# Dados do INMET (estações meteorológicas)
python ingestion/extractors/inmet_extractor.py

# Registrar tabelas no Glue Catalog
python ingestion/loaders/create_glue_tables.py
```

### Transformação com dbt

```bash
cd transformation/air_quality

# Testar conexão com Athena
dbt debug

# Rodar todos os modelos
dbt run

# Rodar testes
dbt test
```

### Airflow

Acesse [http://localhost:8080](http://localhost:8080) com `admin` / `admin`.

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz com:

```env
AWS_ACCESS_KEY_ID=sua_key
AWS_SECRET_ACCESS_KEY=sua_secret
AWS_DEFAULT_REGION=us-east-2
S3_BUCKET=seu-bucket
OPENAQ_API_KEY=sua_key_openaq
```

> **Atenção:** Nunca suba o `.env` para o repositório. Ele está no `.gitignore`.

---

## Roadmap

- [x] Setup AWS (S3, IAM, Glue, Athena)
- [x] Ambiente Docker (Airflow + Spark)
- [x] Extrator OpenAQ v3
- [x] Extrator INMET
- [x] Glue Catalog configurado
- [x] Modelos dbt camada raw
- [ ] Modelos dbt camada silver (limpeza e enriquecimento)
- [ ] Modelos dbt camada gold (métricas analíticas)
- [ ] DAGs Airflow para orquestração
- [ ] Testes dbt (not_null, unique, accepted_values)
- [ ] Great Expectations para validação
- [ ] Dashboard Looker Studio
- [ ] Extrator DataSUS (internações respiratórias)

---

## Licença

MIT
