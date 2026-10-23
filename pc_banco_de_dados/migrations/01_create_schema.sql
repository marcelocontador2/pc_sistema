CREATE TYPE tipo_relatorio AS ENUM ('BALANCETE', 'BALANCO_ORCAMENTARIO', 'BALANCO_FINANCEIRO', 'DFC', 'BALANCO_PATRIMONIAL', 'DVP', 'DMPL');

CREATE TABLE IF NOT EXISTS periodo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ano SMALLINT NOT NULL,
    periodo_acumulado VARCHAR(50) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'ABERTO',
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (ano, periodo_acumulado)
);

CREATE TABLE IF NOT EXISTS documento_importado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    periodo_id UUID NOT NULL REFERENCES periodo(id),
    tipo tipo_relatorio NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    status_processamento VARCHAR(20) DEFAULT 'PENDENTE',
    importado_em TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS balancete_linha (
    id BIGSERIAL PRIMARY KEY,
    documento_id UUID NOT NULL REFERENCES documento_importado(id) ON DELETE CASCADE,
    codigo_conta VARCHAR(50) NOT NULL,
    descricao_conta VARCHAR(255),
    saldo_anterior NUMERIC(18,2) DEFAULT 0.00,
    debito NUMERIC(18,2) DEFAULT 0.00,
    credito NUMERIC(18,2) DEFAULT 0.00,
    saldo_atual NUMERIC(18,2) DEFAULT 0.00,
    natureza_saldo CHAR(1) CHECK (natureza_saldo IN ('D', 'C')),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS demonstracao_resumo (
    id BIGSERIAL PRIMARY KEY,
    documento_id UUID NOT NULL REFERENCES documento_importado(id) ON DELETE CASCADE,
    grupo_demonstrativo VARCHAR(100) NOT NULL,
    valor_atual NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS matriz_calculo (
    id BIGSERIAL PRIMARY KEY,
    periodo_id UUID NOT NULL REFERENCES periodo(id),
    indicador VARCHAR(100) NOT NULL,
    formula_aplicada TEXT,
    valor_resultado NUMERIC(18,4) NOT NULL,
    interpretacao_automatica TEXT,
    gerado_em TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_balancete_conta ON balancete_linha(codigo_conta);
CREATE INDEX IF NOT EXISTS idx_documento_periodo ON documento_importado(periodo_id, tipo);
CREATE INDEX IF NOT EXISTS idx_calculo_indicador ON matriz_calculo(indicador);