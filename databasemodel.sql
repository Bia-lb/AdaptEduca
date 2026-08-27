-- AdaptEduca - esquema compatível com o backend Flask/SQLAlchemy
-- Execute este arquivo em um banco MySQL vazio caso não queira usar db.create_all().
CREATE DATABASE IF NOT EXISTS adapteduca CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE adapteduca;

DROP TABLE IF EXISTS responsavel_turma;
DROP TABLE IF EXISTS aluno_turma;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS adaptacao;
DROP TABLE IF EXISTS relatorio;
DROP TABLE IF EXISTS atividade;
DROP TABLE IF EXISTS conteudo;
DROP TABLE IF EXISTS turma;
DROP TABLE IF EXISTS responsavel;
DROP TABLE IF EXISTS professor;
DROP TABLE IF EXISTS aluno;
DROP TABLE IF EXISTS usuario;

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipoPerfil ENUM('Aluno','Professor','Responsavel') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE aluno (
    id INT PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    preferenciaAprendizagem VARCHAR(80),
    progresso FLOAT DEFAULT 0.0,
    dataNascimento DATE,
    CONSTRAINT fk_aluno_usuario FOREIGN KEY (id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE professor (
    id INT PRIMARY KEY,
    formacao VARCHAR(120),
    disciplina VARCHAR(80),
    CONSTRAINT fk_professor_usuario FOREIGN KEY (id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE responsavel (
    id INT PRIMARY KEY,
    parentesco VARCHAR(40),
    telefone VARCHAR(20),
    CONSTRAINT fk_responsavel_usuario FOREIGN KEY (id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE turma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(80) NOT NULL,
    descricao TEXT,
    professor_id INT NOT NULL,
    CONSTRAINT fk_turma_professor FOREIGN KEY (professor_id) REFERENCES professor(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE aluno_turma (
    aluno_id INT NOT NULL,
    turma_id INT NOT NULL,
    PRIMARY KEY (aluno_id, turma_id),
    CONSTRAINT fk_aluno_turma_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_aluno_turma_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE responsavel_turma (
    responsavel_id INT NOT NULL,
    turma_id INT NOT NULL,
    PRIMARY KEY (responsavel_id, turma_id),
    CONSTRAINT fk_responsavel_turma_responsavel FOREIGN KEY (responsavel_id) REFERENCES responsavel(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_responsavel_turma_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE conteudo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(120) NOT NULL,
    tipo ENUM('Texto','PDF','Video','Link') NOT NULL,
    arquivo VARCHAR(255),
    dataPostagem DATE,
    turma_id INT NOT NULL,
    CONSTRAINT fk_conteudo_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE atividade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(120) NOT NULL,
    descricao TEXT,
    prazo DATE,
    status ENUM('Pendente','Concluida') NOT NULL DEFAULT 'Pendente',
    turma_id INT NOT NULL,
    CONSTRAINT fk_atividade_turma FOREIGN KEY (turma_id) REFERENCES turma(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE adaptacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modo ENUM('Texto simplificado','Audio','Video','Mapa mental','Resumo') NOT NULL,
    resumo TEXT,
    audio BOOLEAN DEFAULT FALSE,
    mapaMental BOOLEAN DEFAULT FALSE,
    conteudo_id INT NOT NULL,
    CONSTRAINT fk_adaptacao_conteudo FOREIGN KEY (conteudo_id) REFERENCES conteudo(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mensagem TEXT NOT NULL,
    data DATE,
    tipo ENUM('Incentivo','Correcao','Orientacao') NOT NULL,
    atividade_id INT NOT NULL,
    CONSTRAINT fk_feedback_atividade FOREIGN KEY (atividade_id) REFERENCES atividade(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE relatorio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    desempenho FLOAT,
    tempoEstudo FLOAT,
    materiasDificeis VARCHAR(255),
    periodo VARCHAR(40),
    aluno_id INT NOT NULL,
    CONSTRAINT fk_relatorio_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Usuários de demonstração utilizados pelos botões "Acesso rápido".
-- Senhas de demonstração: senha123
INSERT INTO usuario (id, nome, email, senha, tipoPerfil) VALUES
(1, 'Prof. João Costa', 'joao.costa@adapteduca.com', 'senha123', 'Professor'),
(2, 'Maria Silva', 'maria.silva@aluno.com', 'senha123', 'Aluno'),
(3, 'Pedro Souza', 'pedro.souza@aluno.com', 'senha123', 'Aluno'),
(4, 'Sr(a). Silva', 'responsavel.silva@gmail.com', 'senha123', 'Responsavel');

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

INSERT INTO atividade (titulo, descricao, prazo, status, turma_id) VALUES
('Equações do 2º Grau', 'Resolver lista de exercícios', '2026-08-15', 'Concluida', 1),
('Geometria Espacial — Introdução', 'Assistir vídeo e responder questionário', '2026-08-20', 'Pendente', 1),
('Análise Sintática', 'Exercício de Português', '2026-08-18', 'Pendente', 1);
