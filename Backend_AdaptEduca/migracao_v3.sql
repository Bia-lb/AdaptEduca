-- Migração v3 (após migracao_v2.sql): conteúdos, adaptações, etapas, feedback,
-- sessões de estudo, vínculo responsável-aluno e relatórios.
-- Execute uma vez: mysql -u root -p adapteduca < migracao_v3.sql
USE adapteduca;

ALTER TABLE conteudo
    ADD COLUMN arquivoOriginal VARCHAR(255) NULL,
    ADD COLUMN texto LONGTEXT NULL;

ALTER TABLE atividade ADD COLUMN etapas TEXT NULL;

ALTER TABLE resposta
    ADD COLUMN etapasConcluidas TEXT NULL,
    ADD COLUMN nota FLOAT NULL;

ALTER TABLE adaptacao
    MODIFY COLUMN modo ENUM('Texto simplificado','Audio','Video','Mapa mental','Resumo','TDAH','TEA','Flashcards') NOT NULL,
    ADD COLUMN resultado LONGTEXT NULL;

ALTER TABLE feedback
    ADD COLUMN aluno_id INT NULL,
    ADD CONSTRAINT fk_feedback_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE relatorio
    ADD COLUMN geradoEm DATETIME NULL,
    ADD COLUMN dados LONGTEXT NULL;

CREATE TABLE IF NOT EXISTS responsavel_aluno (
    responsavel_id INT NOT NULL,
    aluno_id INT NOT NULL,
    PRIMARY KEY (responsavel_id, aluno_id),
    CONSTRAINT fk_resp_aluno_responsavel FOREIGN KEY (responsavel_id) REFERENCES responsavel(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_resp_aluno_aluno FOREIGN KEY (aluno_id) REFERENCES aluno(id)
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

-- ATENÇÃO (privacidade): antes, o responsável enxergava todos os alunos das turmas
-- vinculadas. Agora só vê os filhos em responsavel_aluno. Cada responsável deve
-- vincular o filho na própria conta (matrícula + e-mail do aluno). Para o usuário
-- de demonstração:
INSERT IGNORE INTO responsavel_aluno (responsavel_id, aluno_id) VALUES (4, 2);
