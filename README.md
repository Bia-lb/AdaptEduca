# AdaptEduca — Backend Flask

Plataforma educacional adaptativa. Arquitetura em camadas:
**Models → Repositories → Services → Controllers → Routes → app.py**

---

## Pré-requisitos

- Python 3.10+
- MySQL rodando localmente (usuário `root`, senha `mysqlalkmem`)
- pip

---

## Instalação

```bash
# 1. Clone / descompacte o projeto e entre na pasta
cd adapteduca

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie o banco e popule dados de demonstração
python scripts/seed.py

# 5. Inicie o servidor
python app.py
```

O servidor sobe em **http://localhost:5000**

---

## Dashboard do Responsável

Acesse (após o seed):

```
http://localhost:5000/responsavel/1/dashboard
```

---

## Rotas da API (CRUD completo)

| Método | Endpoint                          | Descrição                     |
|--------|-----------------------------------|-------------------------------|
| GET    | /api/usuarios/                    | Listar usuários               |
| POST   | /api/usuarios/                    | Criar usuário                 |
| GET    | /api/usuarios/<id>                | Buscar usuário                |
| PUT    | /api/usuarios/<id>                | Atualizar usuário             |
| DELETE | /api/usuarios/<id>                | Remover usuário               |
| GET    | /api/alunos/                      | Listar alunos                 |
| POST   | /api/alunos/                      | Criar aluno                   |
| GET    | /api/alunos/<id>                  | Buscar aluno                  |
| PUT    | /api/alunos/<id>                  | Atualizar aluno               |
| DELETE | /api/alunos/<id>                  | Remover aluno                 |
| GET    | /api/turmas/                      | Listar turmas                 |
| POST   | /api/turmas/                      | Criar turma                   |
| GET    | /api/turmas/<id>                  | Buscar turma                  |
| PUT    | /api/turmas/<id>                  | Atualizar turma               |
| DELETE | /api/turmas/<id>                  | Remover turma                 |
| GET    | /api/atividades/                  | Listar atividades             |
| POST   | /api/atividades/                  | Criar atividade               |
| GET    | /api/atividades/<id>              | Buscar atividade              |
| PUT    | /api/atividades/<id>              | Atualizar atividade           |
| DELETE | /api/atividades/<id>              | Remover atividade             |
| GET    | /responsavel/api/                 | Listar responsáveis           |
| POST   | /responsavel/api/                 | Criar responsável             |
| GET    | /responsavel/api/<id>             | Buscar responsável            |
| PUT    | /responsavel/api/<id>             | Atualizar responsável         |
| DELETE | /responsavel/api/<id>             | Remover responsável           |
| GET    | /responsavel/api/<id>/dashboard   | Dashboard JSON do responsável |
| GET    | /responsavel/<id>/dashboard       | Dashboard HTML do responsável |

### Rotas stub (501 Not Implemented — próxima iteração)
- `/api/professores/`
- `/api/conteudos/`
- `/api/adaptacoes/`
- `/api/feedbacks/`
- `/api/relatorios/`

---

## Estrutura do Projeto

```
adapteduca/
├── app.py                        ← Ponto de entrada
├── .env                          ← Variáveis de ambiente
├── requirements.txt
├── README.md
├── scripts/
│   └── seed.py                   ← Cria banco + dados demo
└── app/
    ├── __init__.py               ← Factory (create_app)
    ├── config.py                 ← Configurações por ambiente
    ├── models/
    │   ├── usuario.py            ← STI base
    │   ├── aluno.py
    │   ├── professor.py
    │   ├── responsavel.py
    │   ├── turma.py
    │   ├── conteudo.py
    │   ├── atividade.py
    │   ├── adaptacao.py          ← stub
    │   ├── feedback.py           ← stub
    │   └── relatorio.py          ← stub
    ├── repositories/
    │   ├── base_repository.py    ← Genérico (Generic[T])
    │   ├── usuario_repository.py
    │   ├── aluno_repository.py
    │   ├── turma_repository.py
    │   ├── atividade_repository.py
    │   └── responsavel_repository.py
    ├── services/
    │   ├── usuario_service.py
    │   ├── aluno_service.py
    │   ├── turma_service.py
    │   ├── atividade_service.py
    │   └── responsavel_service.py
    ├── controllers/
    │   ├── base_controller.py    ← Helpers JSON
    │   ├── usuario_controller.py
    │   ├── aluno_controller.py
    │   ├── turma_controller.py
    │   ├── atividade_controller.py
    │   └── responsavel_controller.py
    ├── routes/
    │   ├── usuario_routes.py
    │   ├── aluno_routes.py
    │   ├── turma_routes.py
    │   ├── atividade_routes.py
    │   ├── responsavel_routes.py
    │   └── stub_routes.py
    ├── templates/
    │   ├── base.html
    │   └── responsavel/
    │       └── dashboard.html
    └── static/
        └── css/
            └── adapteduca.css
```

---

## Decisões Técnicas

| Decisão | Justificativa |
|---------|---------------|
| Single Table Inheritance (STI) para Usuario | O UML define herança direta; STI mantém uma FK simples e evita JOINs desnecessários para listagens |
| BaseRepository genérico com Generic[T] | Elimina duplicação de CRUD básico (SRP + DRY) |
| BaseController com helpers JSON | Padroniza todas as respostas: `{sucesso, mensagem, dados}` |
| Stubs retornam 501 | Sinaliza que o endpoint existe no contrato mas não foi implementado, sem quebrar o cliente |
| Senha em texto plano nesta fase | Projeto educacional/demo — adicionar `werkzeug.security` antes de produção |
| Dashboard agregado no Service | Lógica de negócio (cálculo de progresso médio, filhos por turma) pertence ao Service, não ao Controller |
