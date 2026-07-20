# AdaptEduca

## Estrutura

```text
AdaptEduca-final/
├── frontend/
└── backend/
    ├── controllers/
    ├── models/
    ├── repositories/
    ├── services/
    └── database/
        └── create_database.sql
```

## Tecnologias

Frontend em HTML, CSS e JavaScript. Backend em Python com Flask e Flask-SQLAlchemy. Banco de dados SQLite.

## Como executar no Windows

Abra o terminal na pasta `AdaptEduca-final` e execute:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
python backend\app.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

O banco `backend/database/adapteduca.db` já está incluído. O arquivo `backend/database/create_database.sql` contém toda a estrutura SQL para recriá-lo.

## API

A API disponibiliza CRUD para usuários, professores, alunos, responsáveis, turmas, conteúdos, atividades, adaptações, feedbacks e relatórios.

Exemplos:

```text
GET /api/usuarios
POST /api/usuarios
POST /api/auth/login
GET /api/alunos
POST /api/alunos
```
