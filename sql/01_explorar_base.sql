-- Exploracao inicial da base publica do IDEB na Base dos Dados.
-- Objetivo: confirmar tabelas, colunas e se o ano de 2025 ja esta disponivel.

-- 1. Lista de tabelas do conjunto br_inep_ideb
SELECT
    table_name
FROM
    `basedosdados.br_inep_ideb.INFORMATION_SCHEMA.TABLES`
ORDER BY
    table_name;

-- 2. Lista completa de colunas por tabela
SELECT
    table_name,
    column_name,
    data_type
FROM
    `basedosdados.br_inep_ideb.INFORMATION_SCHEMA.COLUMNS`
ORDER BY
    table_name,
    ordinal_position;

-- 3. Anos existentes na tabela principal
SELECT DISTINCT
    ano
FROM
    `basedosdados.br_inep_ideb.brasil`
ORDER BY
    ano DESC;

-- 4. Amostra dos registros de 2023 e 2025, se 2025 ja estiver na tabela
SELECT *
FROM
    `basedosdados.br_inep_ideb.brasil`
WHERE
    ano IN (2023, 2025)
LIMIT 50;
