-- Benchmarks e rankings: Rosario do Catete x Sergipe x DRE 4.
--
-- Status da Base dos Dados em 2026-08-10:
-- `basedosdados.br_inep_ideb.municipio` e `uf` contem dados ate 2023.
-- As colunas de 2025 ficarao nulas ate a incorporacao do arquivo oficial 2025.

WITH dre4 AS (
    SELECT '2801306' AS id_municipio, 'Capela' AS municipio UNION ALL
    SELECT '2801504', 'Carmopolis' UNION ALL
    SELECT '2802007', 'Divina Pastora' UNION ALL
    SELECT '2802502', 'General Maynard' UNION ALL
    SELECT '2803302', 'Japaratuba' UNION ALL
    SELECT '2805307', 'Pirambu' UNION ALL
    SELECT '2806107', 'Rosario do Catete' UNION ALL
    SELECT '2806503', 'Santa Rosa de Lima' UNION ALL
    SELECT '2807204', 'Siriri'
),
municipios_se AS (
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
        i.nota_saeb_media_padronizada,
        i.ideb
    FROM
        `basedosdados.br_inep_ideb.municipio` AS i
    JOIN
        `basedosdados.br_bd_diretorios_brasil.municipio` AS m
        USING (id_municipio)
    WHERE
        i.ano IN (2023, 2025)
        AND i.sigla_uf = 'SE'
        AND i.rede = 'municipal'
        AND i.ensino = 'fundamental'
        AND i.anos_escolares IN ('iniciais (1-5)', 'finais (6-9)')
),
ranking_estadual AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY ano, anos_escolares
            ORDER BY ideb DESC
        ) AS posicao_estadual
    FROM municipios_se
    WHERE ideb IS NOT NULL
),
ranking_dre4 AS (
    SELECT
        r.*,
        RANK() OVER (
            PARTITION BY r.ano, r.anos_escolares
            ORDER BY r.ideb DESC
        ) AS posicao_dre4
    FROM ranking_estadual AS r
    JOIN dre4 USING (id_municipio)
),
sergipe AS (
    SELECT
        ano,
        'Sergipe' AS municipio,
        anos_escolares,
        ideb,
        indicador_rendimento,
        nota_saeb_media_padronizada
    FROM
        `basedosdados.br_inep_ideb.uf`
    WHERE
        ano IN (2023, 2025)
        AND sigla_uf = 'SE'
        AND rede = 'municipal'
        AND ensino = 'fundamental'
        AND anos_escolares IN ('iniciais (1-5)', 'finais (6-9)')
),
rosario_comparativo AS (
    SELECT
        r.id_municipio,
        r.municipio,
        r.anos_escolares,
        MAX(IF(r.ano = 2023, r.ideb, NULL)) AS ideb_2023,
        MAX(IF(r.ano = 2025, r.ideb, NULL)) AS ideb_2025,
        MAX(IF(r.ano = 2023, r.posicao_estadual, NULL)) AS posicao_estadual_2023,
        MAX(IF(r.ano = 2025, r.posicao_estadual, NULL)) AS posicao_estadual_2025,
        MAX(IF(d.ano = 2023, d.posicao_dre4, NULL)) AS posicao_dre4_2023,
        MAX(IF(d.ano = 2025, d.posicao_dre4, NULL)) AS posicao_dre4_2025
    FROM ranking_estadual AS r
    LEFT JOIN ranking_dre4 AS d
        ON r.ano = d.ano
        AND r.id_municipio = d.id_municipio
        AND r.anos_escolares = d.anos_escolares
    WHERE r.id_municipio = '2806107'
    GROUP BY
        r.id_municipio,
        r.municipio,
        r.anos_escolares
),
dre4_2025 AS (
    SELECT
        ano,
        id_municipio,
        municipio,
        anos_escolares,
        ideb,
        posicao_dre4
    FROM ranking_dre4
    WHERE ano = 2025
),
dre4_variacao AS (
    SELECT
        id_municipio,
        municipio,
        anos_escolares,
        MAX(IF(ano = 2023, ideb, NULL)) AS ideb_2023,
        MAX(IF(ano = 2025, ideb, NULL)) AS ideb_2025,
        MAX(IF(ano = 2025, posicao_dre4, NULL)) AS posicao_dre4_2025
    FROM ranking_dre4
    GROUP BY
        id_municipio,
        municipio,
        anos_escolares
),
sergipe_comparativo AS (
    SELECT
        anos_escolares,
        MAX(IF(ano = 2023, ideb, NULL)) AS sergipe_ideb_2023,
        MAX(IF(ano = 2025, ideb, NULL)) AS sergipe_ideb_2025
    FROM sergipe
    GROUP BY anos_escolares
)

-- 1. Resultado principal de Rosario com ranking estadual e DRE 4.
SELECT
    r.*,
    r.ideb_2025 - r.ideb_2023 AS variacao_absoluta,
    SAFE_DIVIDE(r.ideb_2025 - r.ideb_2023, r.ideb_2023) * 100 AS variacao_percentual,
    r.posicao_estadual_2023 - r.posicao_estadual_2025 AS mudanca_posicao_estadual,
    r.posicao_dre4_2023 - r.posicao_dre4_2025 AS mudanca_posicao_dre4,
    s.sergipe_ideb_2023,
    s.sergipe_ideb_2025
FROM rosario_comparativo AS r
LEFT JOIN sergipe_comparativo AS s USING (anos_escolares)
ORDER BY r.anos_escolares;

-- 2. Ranking DRE 4 em 2025.
-- Execute separadamente quando 2025 estiver disponivel.
-- SELECT * FROM dre4_2025 ORDER BY anos_escolares, posicao_dre4;

-- 3. Variacao 2023 x 2025 dos municipios da DRE 4.
-- Execute separadamente quando 2025 estiver disponivel.
-- SELECT
--     *,
--     ideb_2025 - ideb_2023 AS variacao_absoluta,
--     SAFE_DIVIDE(ideb_2025 - ideb_2023, ideb_2023) * 100 AS variacao_percentual
-- FROM dre4_variacao
-- ORDER BY anos_escolares, variacao_absoluta DESC;
