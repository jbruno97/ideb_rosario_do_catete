-- IDEB por escola municipal de Rosario do Catete.
--
-- Status da Base dos Dados em 2026-08-10:
-- `basedosdados.br_inep_ideb.escola` contem dados ate 2023.
-- As colunas de 2025 ficarao nulas ate a incorporacao do arquivo oficial 2025.

WITH escolas_rosario AS (
    SELECT
        i.ano,
        i.sigla_uf,
        i.id_municipio,
        i.id_escola,
        e.nome AS escola,
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
        `basedosdados.br_inep_ideb.escola` AS i
    JOIN
        `basedosdados.br_bd_diretorios_brasil.escola` AS e
        USING (id_escola)
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
        id_escola,
        escola,
        anos_escolares,
        MAX(IF(ano = 2023, ideb, NULL)) AS ideb_2023,
        MAX(IF(ano = 2025, ideb, NULL)) AS ideb_2025,
        MAX(IF(ano = 2023, indicador_rendimento, NULL)) AS indicador_rendimento_2023,
        MAX(IF(ano = 2025, indicador_rendimento, NULL)) AS indicador_rendimento_2025,
        MAX(IF(ano = 2023, nota_saeb_media_padronizada, NULL)) AS desempenho_2023,
        MAX(IF(ano = 2025, nota_saeb_media_padronizada, NULL)) AS desempenho_2025
    FROM escolas_rosario
    GROUP BY
        id_municipio,
        id_escola,
        escola,
        anos_escolares
)
SELECT
    *,
    ideb_2025 - ideb_2023 AS variacao_absoluta,
    SAFE_DIVIDE(ideb_2025 - ideb_2023, ideb_2023) * 100 AS variacao_percentual,
    CASE
        WHEN ideb_2025 - ideb_2023 > 0 THEN 'avanco'
        WHEN ideb_2025 - ideb_2023 < 0 THEN 'queda'
        WHEN ideb_2025 IS NULL THEN 'aguardando_2025'
        ELSE 'estabilidade'
    END AS classificacao_variacao
FROM comparativo
ORDER BY
    anos_escolares,
    variacao_absoluta DESC,
    escola;
