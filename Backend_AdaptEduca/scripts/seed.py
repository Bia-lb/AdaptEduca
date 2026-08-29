"""
Executa: python scripts/seed.py
Cria o banco 'adapteduca' (se não existir) e popula dados de demonstração.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pymysql
from datetime import date
from app import create_app, db
from app.models import Aluno, Professor, Responsavel, Turma, Atividade

# ── Criar banco se não existir ─────────────────────────────────────────────
conn = pymysql.connect(host="localhost", user="root", password="mysqlalkmem")
with conn.cursor() as cur:
    cur.execute("CREATE DATABASE IF NOT EXISTS adapteduca CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
conn.commit()
conn.close()
print("✅ Banco 'adapteduca' verificado/criado.")

# ── Criar tabelas e seed ───────────────────────────────────────────────────
flask_app = create_app("development")

with flask_app.app_context():
    db.create_all()
    print("✅ Tabelas criadas.")

    # Evita duplicação em re-execuções
    if Professor.query.count() > 0:
        print("ℹ️  Dados de seed já existem. Pulando.")
        sys.exit(0)

    # Professor
    prof = Professor(
        nome="Prof. João Costa",
        email="joao.costa@adapteduca.com",
        senha="senha123",
        tipoPerfil="Professor",
        formacao="Licenciatura em Matemática",
        disciplina="Matemática",
    )
    db.session.add(prof)
    db.session.flush()

    # Turma
    turma = Turma(
        codigo="9A-2026",
        nome="9º Ano A",
        descricao="Turma do 9º ano — manhã",
        professor_id=prof.id,
    )
    db.session.add(turma)
    db.session.flush()

    # Alunos
    maria = Aluno(
        nome="Maria Silva",
        email="maria.silva@aluno.com",
        senha="senha123",
        tipoPerfil="Aluno",
        matricula="20260001",
        preferenciaAprendizagem="Visual",
        progresso=85.0,
        dataNascimento=date(2012, 3, 14),
    )
    pedro = Aluno(
        nome="Pedro Souza",
        email="pedro.souza@aluno.com",
        senha="senha123",
        tipoPerfil="Aluno",
        matricula="20260002",
        preferenciaAprendizagem="Auditivo",
        progresso=63.0,
        dataNascimento=date(2011, 9, 22),
    )
    db.session.add_all([maria, pedro])
    db.session.flush()

    turma.alunos.append(maria)
    turma.alunos.append(pedro)

    # Responsável
    responsavel = Responsavel(
        nome="Sr(a). Silva",
        email="responsavel.silva@gmail.com",
        senha="senha123",
        tipoPerfil="Responsavel",
        parentesco="Mãe",
        telefone="(31) 99999-0001",
    )
    db.session.add(responsavel)
    db.session.flush()

    responsavel.turmas.append(turma)

    # Atividades
    at1 = Atividade(
        titulo="Equações do 2º Grau",
        descricao="Resolver lista de exercícios",
        prazo=date(2026, 8, 15),
        status="Concluida",
        turma_id=turma.id,
    )
    at2 = Atividade(
        titulo="Geometria Espacial — Introdução",
        descricao="Assistir vídeo e responder questionário",
        prazo=date(2026, 8, 20),
        status="Pendente",
        turma_id=turma.id,
    )
    at3 = Atividade(
        titulo="Análise Sintática",
        descricao="Exercício de Português",
        prazo=date(2026, 8, 18),
        status="Pendente",
        turma_id=turma.id,
    )
    db.session.add_all([at1, at2, at3])

    db.session.commit()
    print("✅ Dados de seed inseridos com sucesso!")
    print()
    print("🔗 Dashboard do Responsável:")
    print(f"   http://localhost:5000/responsavel/{responsavel.id}/dashboard")
