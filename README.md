# CEPEA Price Analytics — pronto para leigos

Solução completa para **coletar diariamente** (após 18h BRT), **armazenar** em Postgres e **visualizar** em **Streamlit** as variações de preços do CEPEA/ESALQ.

> **Licença de dados**: CEPEA/ESALQ/USP — **CC BY-NC 4.0** (uso **não comercial** com crédito). Para usos comerciais, contate o CEPEA.

## Como publicar sem ser dev (4 passos)

### 1) Crie um Postgres **grátis** (Neon)
- Crie uma conta em neon.tech (free tier) e gere um database.
- Copie a URL no formato: `postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME`

### 2) Crie um repositório no GitHub
- Baixe este ZIP e faça o upload dos arquivos no seu repositório.
- Em **Settings → Secrets → Actions**, crie o **secret** `DATABASE_URL` com a URL do Postgres.

### 3) Habilite o agendamento
- Este repositório já traz um **GitHub Action** que roda **todo dia às 18:30 BRT**.
- Ele baixa os Excels da página de **Consultas do CEPEA** e carrega no Postgres.

### 4) Publique o app no **Streamlit Community Cloud**
- Acesse share.streamlit.io → "Deploy an app" → selecione seu repo
- **Main file path**: `app/streamlit_app.py`
- Em **Advanced settings → Secrets**, cole o mesmo `DATABASE_URL`.
- Publique.

## Uso manual (opcional)
- Rodar ETL local: `python etl/extract_cepea_consultas.py && DATABASE_URL=... python etl/load_normalize.py`
- Rodar app local: `DATABASE_URL=... streamlit run app/streamlit_app.py`

## Ajustes importantes
- O HTML da página de **Consultas** do CEPEA pode mudar. Se quebrar, edite seletores em `etl/extract_cepea_consultas.py` (linhas comentadas).
- Para histórico (várias datas), defina `ETL_DATE_FROM` e `ETL_DATE_TO` (YYYY-MM-DD) no step "ETL - Extract".

## O que está incluído
- **/app/streamlit_app.py**: front-end com **cards** (D/D-1, 30/180/360d) e **gráficos**.
- **/etl/extract_cepea_consultas.py**: baixa Excel via **Playwright**.
- **/etl/load_normalize.py**: normaliza colunas e grava no Postgres; atualiza a **view** de variações.
- **/db/schema.sql**: tabelas e materialized view.
- **/.github/workflows/etl.yml**: agendamento diário 18:30 BRT.

## Créditos
- Dados: **CEPEA/ESALQ/USP** — cite a fonte e respeite a licença **CC BY-NC 4.0**.

*Pacote gerado em 2025-10-27.*
