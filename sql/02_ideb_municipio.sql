-- IDEB de Rosario do Catete - rede municipal - ensino fundamental.
--
-- Status da Base dos Dados em 2026-08-10:
-- `basedosdados.br_inep_ideb.municipio` contem dados ate 2023.
-- Quando o IDEB 2025 oficial for carregado no projeto, una a tabela 2025
-- no CTE `dados` mantendo estes nomes de colunas.

WITH dados AS (
    SELECT
        i.ano,
        i.sigla_uf,
        i.id_municipio,
        m.nome AS municipio,
        i.rede,
        i.ensino,
        i.anos_escolares,
        i.taxa_aprovacao,
        i.indicador_rendimento,
        i.nota_saeb_matematica,
        i.nota_saeb_lingua_portuguesa,
        i.nota_saeb_media_padronizada,
        i.ideb,
        i.projecao
    FROM
        `basedosdados.br_inep_ideb.municipio` AS i
    JOIN
        `basedosdados.br_bd_diretorios_brasil.municipio` AS m
        USING (id_municipio)
    WHERE
        i.ano IN (2023, 2025)
        AND i.id_municipio = '2806107'
        AND i.rede = 'municipal'
        AND i.ensino = 'fundamental'
        AND i.anos_escolares IN ('iniciais (1-5)', 'finais (6-9)')
),
comparativo AS (
    SELECT
        id_municipio,
        municipio,
        anos_escolares,
        MAX(IF(ano = 2023, ideb, NULL)) AS ideb_2023,
        MAX(IF(ano = 2025, ideb, NULL)) AS ideb_2025,
        MAX(IF(ano = 2023, taxa_aprovacao, NULL)) AS taxa_aprovacao_2023,
        MAX(IF(ano = 2025, taxa_aprovacao, NULL)) AS taxa_aprovacao_2025,
        MAX(IF(ano = 2023, indicador_rendimento, NULL)) AS indicador_rendimento_2023,
        MAX(IF(ano = 2025, indicador_rendimento, NULL)) AS indicador_rendimento_2025,
        MAX(IF(ano = 2023, nota_saeb_media_padronizada, NULL)) AS desempenho_2023,
        MAX(IF(ano = 2025, nota_saeb_media_padronizada, NULL)) AS desempenho_2025
    FROM dados
    GROUP BY
        id_municipio,
        municipio,
        anos_escolares
)
SELECT
    *,
    ideb_2025 - ideb_2023 AS variacao_absoluta,
    SAFE_DIVIDE(ideb_2025 - ideb_2023, ideb_2023) * 100 AS variacao_percentual,
    indicador_rendimento_2025 - indicador_rendimento_2023 AS variacao_rendimento,
    desempenho_2025 - desempenho_2023 AS variacao_desempenho
FROM comparativo
ORDER BY
    anos_escolares;
