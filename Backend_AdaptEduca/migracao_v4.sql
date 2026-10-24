-- Agentes de IA: controle de uso diário por usuário.
-- Rode uma vez em bancos criados antes desta versão.
USE adapteduca;

CREATE TABLE IF NOT EXISTS ia_uso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    dia DATE NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_ia_uso_usuario_dia UNIQUE (usuario_id, dia),
    CONSTRAINT fk_ia_uso_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
