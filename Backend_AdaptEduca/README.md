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


## Atualização: fluxo central (RF04, RF05, RF12, RF15)

Banco já existente? Rode `migracao_v2.sql`. Banco novo: `databasemodel.sql`.

- Senhas gravadas como hash; senhas antigas em texto puro migram no primeiro login.
- Login/cadastro devolvem `token` (Bearer). Todas as rotas exceto `/api/auth/login`, `/api/auth/register` e `/api/health` exigem o token, com controle por perfil.
- `PUT /api/alunos/me/questionario` salva o questionário (RF04). `GET /api/alunos/me` devolve o perfil completo do próprio aluno.
- Turmas: `POST /api/turmas/`, `GET|POST /api/turmas/<id>/alunos`, `DELETE /api/turmas/<id>/alunos/<aluno_id>` (RF05).
- Atividades com prazo e questões; `PUT /api/atividades/<id>/resposta` (rascunho ou envio) e `GET /api/atividades/<id>/respostas` (RF12, RF15).
- Em produção defina `SECRET_KEY`. Testes: `pip install pytest && python -m pytest tests`.


## Atualização: todos os requisitos (RF03, RF06–RF11, RF13, RF14, RF16–RF20)

Bancos existentes: rode `migracao_v2.sql` e depois `migracao_v3.sql`. Banco novo: `databasemodel.sql`.
Dependências: `pip install -r requirements.txt` (inclui `pypdf`). Testes: `pip install -r requirements-dev.txt && python -m pytest tests`.

| RF | Onde |
|----|------|
| 03 | `POST /api/auth/esqueci-senha` e `/redefinir-senha` (link de 1 h, uso único). Sem `MAIL_HOST` o e-mail aparece no console do Flask; para enviar de verdade configure `MAIL_HOST`, `MAIL_PORT`, `MAIL_USER`, `MAIL_PASSWORD`, `MAIL_FROM` e `FRONTEND_URL` |
| 06 | `/api/conteudos/` — texto, link ou PDF (o texto do PDF é extraído; PDFs escaneados como imagem não funcionam) |
| 07, 08, 10, 13 | `GET /api/conteudos/<id>/adaptacao?modo=resumo\|simplificado\|tdah\|tea\|mapa\|flashcards\|para-mim` — `para-mim` escolhe o formato pelo questionário do aluno |
| 09 | modo `audio`: segmentos de texto; a voz é a do navegador (SpeechSynthesis, pt-BR) |
| 11 | atividades com `etapas`; o progresso das etapas é salvo e o envio exige todas concluídas |
| 14 | `/api/estudo/modos` e `/api/estudo/sessoes` (Leitura, Foco com timer, Revisão, Áudio) |
| 16, 17, 19 | `/api/progresso/aluno/<id>`, `/api/progresso/professor`, `/api/progresso/responsavel` |
| 18 | `/api/feedbacks/` (mensagem + nota de 0 a 10) |
| 20 | `/api/relatorios/aluno/<id>` (gera e salva) e `/api/relatorios/<id>` |

Observações:
- A adaptação é feita por regras de processamento de texto em português (sem IA externa): resumo extrativo, simplificação de frases e conectivos, blocos curtos para TDAH, estrutura literal e glossário para TEA, mapa mental por termos-chave. É determinística e funciona offline; para qualidade de IA generativa, `app/services/adaptacao_engine.py` é o ponto de troca.
- O responsável só vê filhos vinculados por matrícula + e-mail do aluno (`/api/responsaveis/me/filhos`). Antes, via todos os alunos da turma.
