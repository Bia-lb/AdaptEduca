# AdaptEduca — Backend + Frontend integrado

## Arquitetura

A implementação segue a arquitetura solicitada na disciplina:

**Routes → Controllers → Services → Models → banco**

- **Models:** herdam de `db.Model` e possuem os métodos CRUD (`listar`, `buscar_por_id`, `criar`, `atualizar`, `deletar`).
- **Repositories:** não fazem CRUD com ORM/Query Builder. São reservados para consultas SQL explícitas, principalmente consultas específicas/complexas.
- **SQL:** `databasemodel.sql` é o schema oficial do projeto.
- **Frontend:** consome os endpoints REST através de `js/api.js` usando `fetch`.

## Banco de dados

1. Abra `databasemodel.sql` no MySQL Workbench.
2. Execute o arquivo completo.
3. Confira as credenciais em `.env` (copie `.env.example` para `.env`).

Por padrão:

```text
host=localhost
port=3306
user=root
password=
database=adapteduca
```

## Backend

Dentro de `Backend_AdaptEduca/Backend_AdaptEduca`:

```bash
pip install -r requirements.txt
python app.py
```

Teste:

```text
http://localhost:5000/api/health
```

O resultado esperado é um JSON informando que a API e o MySQL estão conectados.

## Frontend

O frontend fica em `Frontend_AdaptEduca/Frontend_AdaptEduca`.

Ele já usa `fetch` para:

- login: `POST /api/auth/login`
- cadastro: `POST /api/auth/register`
- alunos: `GET /api/alunos/`
- turmas: `GET /api/turmas/`
- atividades: `GET /api/atividades/`
- dashboard do responsável: `GET /responsavel/api/<id>/dashboard`

O `js/api.js` usa `http://localhost:5000/api` quando o HTML é aberto diretamente e usa a mesma origem quando o frontend for servido pelo Flask.

Para abrir o frontend por um servidor local, dentro da pasta do frontend:

```bash
python -m http.server 5500
```

Depois abra `http://localhost:5500/login.html` com o backend rodando na porta 5000.
