-- Migração para bancos já criados com a versão anterior do esquema.
-- Execute uma vez: mysql -u root -p adapteduca < migracao_v2.sql
USE adapteduca;

ALTER TABLE aluno
    ADD COLUMN questionario TEXT NULL,
    ADD COLUMN questionarioConcluido BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE atividade
    ADD COLUMN questoes TEXT NULL;

CREATE TABLE IF NOT EXISTS resposta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    atividade_id INT NOT NULL,
    aluno_id INT NOT NULL,
    respostas TEXT,
    status ENUM('Em andamento','Enviada') NOT NULL DEFAULT 'Em andamento',
    atualizadaEm DATETIME,
    enviadaEm DATETIME,
    CONSTRAINT uq_resposta_atividade_aluno UNIQUE (atividade_id, aluno_id),
    CONSTRAINT fk_resposta_atividade FOREIGN KEY (atividade_id) REFERENCES atividade(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_resposta_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Senhas antigas em texto puro continuam funcionando: o backend converte
-- cada uma para hash no primeiro login bem-sucedido do usuário.
