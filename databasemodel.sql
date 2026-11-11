-- ADAPTEDUCA - BANCO PRINCIPAL UNIFICADO
-- Arquivos integrados: databasemodel.sql, adapteduca.sql, correçoes.sql.
-- Serve para banco novo OU banco ja existente.
-- NAO APAGA tabelas, contas, atividades ou dados atuais.
-- Recomendado: exportar backup antes de executar.
-- Contas de demonstracao sao inseridas SOMENTE se a tabela usuario estiver vazia.

CREATE DATABASE IF NOT EXISTS adapteduca
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE adapteduca;

-- 1. Criacao de todas as tabelas, com todas as colunas consolidadas.
-- CREATE TABLE IF NOT EXISTS preserva tabelas existentes.

CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipoPerfil ENUM('Aluno','Professor','Responsavel') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aluno (
    id INT PRIMARY KEY,
    matricula VARCHAR(50) NOT NULL UNIQUE,
    preferenciaAprendizagem VARCHAR(80),
    progresso FLOAT DEFAULT 0.0,
    dataNascimento DATE,
    questionario TEXT,
    questionarioConcluido BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_aluno_usuario FOREIGN KEY (id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS professor (
    id INT PRIMARY KEY,
    formacao VARCHAR(120),
    disciplina VARCHAR(80),
    CONSTRAINT fk_professor_usuario FOREIGN KEY (id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS responsavel (
    id INT PRIMARY KEY,
    parentesco VARCHAR(40),
    telefone VARCHAR(20),
    CONSTRAINT fk_responsavel_usuario FOREIGN KEY (id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS turma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(80) NOT NULL,
    descricao TEXT,
    professor_id INT NOT NULL,
    CONSTRAINT fk_turma_professor FOREIGN KEY (professor_id) REFERENCES professor(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aluno_turma (
    aluno_id INT NOT NULL,
    turma_id INT NOT NULL,
    PRIMARY KEY (aluno_id, turma_id),
    CONSTRAINT fk_aluno_turma_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_aluno_turma_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS responsavel_turma (
    responsavel_id INT NOT NULL,
    turma_id INT NOT NULL,
    PRIMARY KEY (responsavel_id, turma_id),
    CONSTRAINT fk_responsavel_turma_responsavel FOREIGN KEY (responsavel_id) REFERENCES responsavel(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_responsavel_turma_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS responsavel_aluno (
    responsavel_id INT NOT NULL,
    aluno_id INT NOT NULL,
    PRIMARY KEY (responsavel_id, aluno_id),
    CONSTRAINT fk_resp_aluno_responsavel FOREIGN KEY (responsavel_id) REFERENCES responsavel(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_resp_aluno_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS conteudo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(120) NOT NULL,
    tipo ENUM('Texto','PDF','Video','Link') NOT NULL,
    arquivo VARCHAR(255),
    arquivoOriginal VARCHAR(255),
    texto LONGTEXT,
    dataPostagem DATE,
    linkExterno VARCHAR(2048) NULL,
    turma_id INT NOT NULL,
    CONSTRAINT fk_conteudo_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS atividade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(120) NOT NULL,
    descricao TEXT,
    prazo DATE,
    status ENUM('Pendente','Concluida') NOT NULL DEFAULT 'Pendente',
    turma_id INT NOT NULL,
    questoes TEXT,
    etapas TEXT,
    pdfArquivo LONGTEXT NULL,
    pdfOriginal LONGTEXT NULL,
    links TEXT NULL,
    CONSTRAINT fk_atividade_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS resposta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    atividade_id INT NOT NULL,
    aluno_id INT NOT NULL,
    respostas TEXT,
    status ENUM('Em andamento','Enviada') NOT NULL DEFAULT 'Em andamento',
    etapasConcluidas TEXT,
    nota FLOAT,
    atualizadaEm DATETIME,
    enviadaEm DATETIME,
    CONSTRAINT uq_resposta_atividade_aluno UNIQUE (atividade_id, aluno_id),
    CONSTRAINT fk_resposta_atividade FOREIGN KEY (atividade_id) REFERENCES atividade(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_resposta_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sessao_estudo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    conteudo_id INT NULL,
    modo VARCHAR(30) NOT NULL,
    segundos INT NOT NULL,
    iniciadaEm DATETIME NOT NULL,
    CONSTRAINT fk_sessao_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sessao_conteudo FOREIGN KEY (conteudo_id) REFERENCES conteudo(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Agentes de IA: contador diário de chamadas por usuário
CREATE TABLE IF NOT EXISTS ia_uso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    dia DATE NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_ia_uso_usuario_dia UNIQUE (usuario_id, dia),
    CONSTRAINT fk_ia_uso_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS adaptacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modo ENUM('Texto simplificado','Audio','Video','Mapa mental','Resumo','TDAH','TEA','Flashcards') NOT NULL,
    resumo TEXT,
    resultado LONGTEXT,
    audio BOOLEAN DEFAULT FALSE,
    mapaMental BOOLEAN DEFAULT FALSE,
    conteudo_id INT NOT NULL,
    CONSTRAINT fk_adaptacao_conteudo FOREIGN KEY (conteudo_id) REFERENCES conteudo(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mensagem TEXT NOT NULL,
    data DATE,
    tipo ENUM('Incentivo','Correcao','Orientacao') NOT NULL,
    atividade_id INT NOT NULL,
    aluno_id INT NULL,
    CONSTRAINT fk_feedback_atividade FOREIGN KEY (atividade_id) REFERENCES atividade(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_feedback_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS relatorio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    desempenho FLOAT,
    tempoEstudo FLOAT,
    materiasDificeis VARCHAR(255),
    periodo VARCHAR(40),
    geradoEm DATETIME,
    dados LONGTEXT,
    aluno_id INT NOT NULL,
    CONSTRAINT fk_relatorio_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- 2. Aplicar, apenas quando faltarem, as colunas dos SQLs complementares
-- em bancos que ja tinham sido criados com o esquema antigo.
DELIMITER $$
DROP PROCEDURE IF EXISTS adapteduca_atualizar_coluna$$
CREATE PROCEDURE adapteduca_atualizar_coluna(
    IN p_tabela VARCHAR(64), IN p_coluna VARCHAR(64), IN p_definicao VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = p_tabela
          AND COLUMN_NAME = p_coluna
    ) THEN
        SET @ddl = CONCAT('ALTER TABLE `',p_tabela,'` ADD COLUMN `',p_coluna,'` ',p_definicao);
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

CALL adapteduca_atualizar_coluna('atividade','pdfArquivo','LONGTEXT NULL');
CALL adapteduca_atualizar_coluna('atividade','pdfOriginal','LONGTEXT NULL');
CALL adapteduca_atualizar_coluna('atividade','links','TEXT NULL');
CALL adapteduca_atualizar_coluna('conteudo','linkExterno','VARCHAR(2048) NULL');
DROP PROCEDURE IF EXISTS adapteduca_atualizar_coluna;

-- Amplia matricula para 50 caracteres. Preserva matriculas cadastradas.
ALTER TABLE aluno MODIFY COLUMN matricula VARCHAR(50) NOT NULL;

-- 3. Usuarios e dados demonstrativos que constavam no codigo principal.
-- Insere o conjunto completo apenas se ainda NAO existe nenhum usuario.
-- Assim nao recria contas apagadas e nao duplica registros em banco existente.
DELIMITER $$
DROP PROCEDURE IF EXISTS adapteduca_inserir_demonstracao$$
CREATE PROCEDURE adapteduca_inserir_demonstracao()
BEGIN
    IF NOT EXISTS (SELECT 1 FROM usuario LIMIT 1) THEN
    INSERT INTO usuario (id, nome, email, senha, tipoPerfil) VALUES
    (1, 'Prof. João Costa', 'joao.costa@adapteduca.com', 'pbkdf2:sha256:1000000$akqG5qcZjik0hYSG$0947b132256661777cf766c41b674210ac7a78085ff2672148f46b99eec1f284', 'Professor'),
    (2, 'Maria Silva', 'maria.silva@aluno.com', 'pbkdf2:sha256:1000000$akqG5qcZjik0hYSG$0947b132256661777cf766c41b674210ac7a78085ff2672148f46b99eec1f284', 'Aluno'),
    (3, 'Pedro Souza', 'pedro.souza@aluno.com', 'pbkdf2:sha256:1000000$akqG5qcZjik0hYSG$0947b132256661777cf766c41b674210ac7a78085ff2672148f46b99eec1f284', 'Aluno'),
    (4, 'Sr(a). Silva', 'responsavel.silva@gmail.com', 'pbkdf2:sha256:1000000$akqG5qcZjik0hYSG$0947b132256661777cf766c41b674210ac7a78085ff2672148f46b99eec1f284', 'Responsavel');

    INSERT INTO professor (id, formacao, disciplina) VALUES
    (1, 'Licenciatura em Matemática', 'Matemática');

    INSERT INTO aluno (id, matricula, preferenciaAprendizagem, progresso, dataNascimento) VALUES
    (2, '20260001', 'Visual', 85.0, '2012-03-14'),
    (3, '20260002', 'Auditivo', 63.0, '2011-09-22');

    INSERT INTO responsavel (id, parentesco, telefone) VALUES
    (4, 'Mãe', '(31) 99999-0001');

    INSERT INTO turma (id, codigo, nome, descricao, professor_id) VALUES
    (1, '9A-2026', '9º Ano A', 'Turma do 9º ano — manhã', 1);

    INSERT INTO aluno_turma (aluno_id, turma_id) VALUES (2,1),(3,1);
    INSERT INTO responsavel_turma (responsavel_id, turma_id) VALUES (4,1);
    INSERT INTO responsavel_aluno (responsavel_id, aluno_id) VALUES (4,2);

    INSERT INTO atividade (titulo, descricao, prazo, status, turma_id) VALUES
    ('Equações do 2º Grau', 'Resolver lista de exercícios', '2026-08-15', 'Concluida', 1),
    ('Geometria Espacial — Introdução', 'Assistir vídeo e responder questionário', '2026-08-20', 'Pendente', 1),
    ('Análise Sintática', 'Exercício de Português', '2026-08-18', 'Pendente', 1);
    END IF;
END$$
DELIMITER ;
CALL adapteduca_inserir_demonstracao();
DROP PROCEDURE IF EXISTS adapteduca_inserir_demonstracao;

-- 4. Verificacao final, sem alterar informacoes.
SHOW TABLES;
SHOW COLUMNS FROM atividade;
SHOW COLUMNS FROM conteudo;
SHOW COLUMNS FROM aluno;
SELECT id, nome, email, tipoPerfil FROM usuario ORDER BY id;
