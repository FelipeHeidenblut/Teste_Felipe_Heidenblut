CREATE DATABASE IF NOT EXISTS ans_teste
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE ans_teste;

-- Tabela de despesas consolidadas
DROP TABLE IF EXISTS despesas_consolidadas;
CREATE TABLE despesas_consolidadas (
    REG_ANS         VARCHAR(20),
    CNPJ            VARCHAR(20),
    RazaoSocial     VARCHAR(255),
    Modalidade      VARCHAR(100),
    UF              CHAR(2),
    Ano             INT,
    Trimestre       VARCHAR(10),
    ValorDespesas   DECIMAL(18,2),
    ValorDespesas_num DECIMAL(18,2),
    flag_valor_invalido          TINYINT(1),
    flag_valor_negativo_ou_zero  TINYINT(1),
    flag_sem_cadastro            TINYINT(1),
    flag_reg_ans_duplicado_cad   TINYINT(1),
    flag_cnpj_invalido           TINYINT(1),
    flag_razao_vazia             TINYINT(1)
);

-- Tabela de cadastro das operadoras
DROP TABLE IF EXISTS operadoras_cadastro;
CREATE TABLE operadoras_cadastro (
    REG_ANS             VARCHAR(20),
    CNPJ                VARCHAR(20),
    Razao_Social        VARCHAR(255),
    Nome_Fantasia       VARCHAR(255),
    Modalidade          VARCHAR(100),
    UF                  CHAR(2)
    
);

-- Tabela de despesas agregadas
DROP TABLE IF EXISTS despesas_agregadas;
CREATE TABLE despesas_agregadas (
    RazaoSocial     VARCHAR(255),
    UF              CHAR(2),
    TotalDespesas   DECIMAL(18,2),
    MediaDespesas   DECIMAL(18,2),
    DesvioPadrao    DECIMAL(18,2)
);

-- Índices para otimização de consultas
CREATE INDEX idx_desp_reg_ans ON despesas_consolidadas (REG_ANS);
CREATE INDEX idx_desp_razao_uf ON despesas_consolidadas (RazaoSocial, UF);

-- =========================================

-- 2.1 Importar consolidado validado final
LOAD DATA LOCAL INFILE '/caminho/para/consolidado_despesas_validado_final.csv'
INTO TABLE despesas_consolidadas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    REG_ANS,
    ValorDespesas,
    Ano,
    Trimestre,
    flag_valor_zero_ou_negativo,
    CNPJ,
    RazaoSocial,
    Modalidade,
    UF,
    flag_sem_cadastro,
    flag_reg_ans_duplicado_cad,
    ValorDespesas_num,
    flag_valor_invalido,
    flag_valor_negativo_ou_zero,
    @CNPJ_limpo,
    flag_cnpj_invalido,
    flag_razao_vazia
);

-- 2.2 Importar cadastro simplificado
LOAD DATA LOCAL INFILE '/caminho/para/Relatorio_cadop.csv'
INTO TABLE operadoras_cadastro
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    REG_ANS,
    CNPJ,
    Razao_Social,
    Nome_Fantasia,
    Modalidade,
    @Logradouro,
    @Numero,
    @Complemento,
    @Bairro,
    @Cidade,
    UF,
    @resto
);

-- 2.3 Importar despesas agregadas
LOAD DATA LOCAL INFILE '/caminho/para/despesas_agregadas.csv'
INTO TABLE despesas_agregadas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(RazaoSocial, UF, TotalDespesas, MediaDespesas, DesvioPadrao);


-- =========================================

-- Query 1: 5 operadoras com maior crescimento percentual
-- (entre o primeiro e o último trimestre existentes)

WITH totais_por_tri AS (
    SELECT
        RazaoSocial,
        UF,
        Ano,
        Trimestre,
        SUM(ValorDespesas_num) AS total_tri
    FROM despesas_consolidadas
    WHERE ValorDespesas_num IS NOT NULL
    GROUP BY RazaoSocial, UF, Ano, Trimestre
),
primeiro_ultimo AS (
    SELECT
        RazaoSocial,
        UF,
        MIN(CONCAT(Ano, '_', Trimestre)) AS primeiro,
        MAX(CONCAT(Ano, '_', Trimestre)) AS ultimo
    FROM totais_por_tri
    GROUP BY RazaoSocial, UF
),
totais_comparados AS (
    SELECT
        p.RazaoSocial,
        p.UF,
        tp1.total_tri AS total_primeiro,
        tp2.total_tri AS total_ultimo
    FROM primeiro_ultimo p
    JOIN totais_por_tri tp1
      ON tp1.RazaoSocial = p.RazaoSocial
     AND tp1.UF = p.UF
     AND CONCAT(tp1.Ano, '_', tp1.Trimestre) = p.primeiro
    JOIN totais_por_tri tp2
      ON tp2.RazaoSocial = p.RazaoSocial
     AND tp2.UF = p.UF
     AND CONCAT(tp2.Ano, '_', tp2.Trimestre) = p.ultimo
)
SELECT
    RazaoSocial,
    UF,
    total_primeiro,
    total_ultimo,
    CASE
        WHEN total_primeiro > 0 THEN (total_ultimo - total_primeiro) / total_primeiro * 100
        ELSE NULL
    END AS crescimento_percentual
FROM totais_comparados
ORDER BY crescimento_percentual DESC
LIMIT 5;


-- Query 2: distribuição de despesas por UF (top 5) + média por operadora

-- 2.1 Top 5 UFs por total de despesas
SELECT
    UF,
    SUM(ValorDespesas_num) AS total_despesas_uf
FROM despesas_consolidadas
WHERE ValorDespesas_num IS NOT NULL
GROUP BY UF
ORDER BY total_despesas_uf DESC
LIMIT 5;

-- 2.2 Média de despesas por operadora em cada UF
SELECT
    UF,
    RazaoSocial,
    SUM(ValorDespesas_num) AS total_operadora_uf,
    AVG(ValorDespesas_num) AS media_operadora_uf
FROM despesas_consolidadas
WHERE ValorDespesas_num IS NOT NULL
GROUP BY UF, RazaoSocial
ORDER BY UF, total_operadora_uf DESC;


-- Query 3: operadoras com despesas acima da média geral em pelo menos 2 trimestres

WITH media_geral_tri AS (
    SELECT
        Ano,
        Trimestre,
        AVG(ValorDespesas_num) AS media_tri
    FROM despesas_consolidadas
    WHERE ValorDespesas_num IS NOT NULL
    GROUP BY Ano, Trimestre
),
totais_operadora_tri AS (
    SELECT
        RazaoSocial,
        UF,
        Ano,
        Trimestre,
        SUM(ValorDespesas_num) AS total_operadora_tri
    FROM despesas_consolidadas
    WHERE ValorDespesas_num IS NOT NULL
    GROUP BY RazaoSocial, UF, Ano, Trimestre
),
comparacao AS (
    SELECT
        t.RazaoSocial,
        t.UF,
        t.Ano,
        t.Trimestre,
        t.total_operadora_tri,
        m.media_tri,
        CASE
            WHEN t.total_operadora_tri > m.media_tri THEN 1
            ELSE 0
        END AS acima_da_media
    FROM totais_operadora_tri t
    JOIN media_geral_tri m
      ON m.Ano = t.Ano
     AND m.Trimestre = t.Trimestre
)
SELECT
    RazaoSocial,
    UF,
    SUM(acima_da_media) AS qtde_trimestres_acima_media
FROM comparacao
GROUP BY RazaoSocial, UF
HAVING SUM(acima_da_media) >= 2;