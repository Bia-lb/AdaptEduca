# AdaptEduca — Projeto completo consolidado

Front-end completo da plataforma **AdaptEduca**, desenvolvido exclusivamente com HTML5, CSS3 e JavaScript puro.

Nesta entrega, **todas as 28 páginas HTML estão diretamente dentro de uma única pasta principal**, sem a antiga subpasta `pages`. Os arquivos de estilo, scripts, imagens, componentes e documentos permanecem organizados em subpastas próprias.

## Como executar

### Live Server — recomendado

1. Extraia a pasta `AdaptEduca_Projeto_Completo`.
2. Abra a pasta no Visual Studio Code.
3. Clique com o botão direito em `index.html`.
4. Selecione **Open with Live Server**.

Também é possível executar pelo terminal dentro da pasta:

```bash
python -m http.server 8000
```

Depois acesse `http://localhost:8000`.

## Credenciais de demonstração

Todas as contas usam a senha `123456`.

| Perfil | E-mail |
|---|---|
| Aluno | `aluno@adapteduca.com` |
| Professor | `professor@adapteduca.com` |
| Responsável | `responsavel@adapteduca.com` |

## Páginas incluídas

### Área pública

- `index.html` — Página inicial;
- `funcionalidades.html` — Funcionalidades;
- `demo.html` — Demonstração dos requisitos;
- `planos.html` — Planos e preços;
- `login.html` — Login;
- `cadastro.html` — Cadastro.

### Área do aluno

- `questionario-aluno.html` — Perfil de aprendizagem em nove etapas;
- `dashboard-aluno.html` — Painel do aluno;
- `conteudos-aluno.html` — Biblioteca de conteúdos;
- `atividades-aluno.html` — Atividades;
- `historico-aluno.html` — Histórico;
- `perfil-aluno.html` — Perfil e preferências;
- `adaptacao-conteudo.html` — Adaptação de conteúdo com IA simulada.

### Área do professor

- `dashboard-professor.html` — Painel do professor;
- `turmas.html` — Turmas;
- `alunos.html` — Alunos;
- `enviar-conteudo.html` — Envio de conteúdo;
- `materiais.html` — Gerenciamento de materiais;
- `atividades-professor.html` — Atividades;
- `relatorios-professor.html` — Relatórios;
- `configuracoes-professor.html` — Configurações.

### Área do responsável

- `dashboard-responsavel.html` — Painel do responsável;
- `acompanhamento.html` — Acompanhamento dos alunos;
- `desempenho.html` — Desempenho;
- `progresso-responsavel.html` — Progresso;
- `relatorios-responsavel.html` — Relatórios;
- `comunicados.html` — Mensagens e comunicados;
- `configuracoes-responsavel.html` — Configurações.

## Funcionalidades

- Tema claro e escuro persistido no `localStorage`;
- Cadastro, login, sessão e logout simulados;
- Proteção de páginas privadas;
- Controle de acesso por aluno, professor e responsável;
- Redirecionamento do aluno para o questionário quando necessário;
- Questionário multi-etapas com salvamento temporário;
- Dashboards baseados nos prints enviados;
- Adaptação de conteúdo em resumo, mapa mental, áudio, TDAH, TEA e texto simplificado;
- Chat com IA simulado;
- Pesquisa, filtros, abas, modais, notificações e formulários;
- Layout responsivo para desktop, notebook, tablet e smartphone;
- Estrutura preparada para integração futura com PHP e MySQL.

## Estrutura da pasta

```text
AdaptEduca_Projeto_Completo/
├── todos-os-arquivos-html-aqui
├── css/
├── js/
├── img/
├── components/
├── docs/
├── README.md
├── QA_REPORT.md
└── favicon.ico
```

## Armazenamento simulado

- `adapteduca_users` — contas cadastradas;
- `adapteduca_session` — sessão ativa;
- `adapteduca_theme` — tema escolhido;
- `adapteduca_questionnaire_draft` — rascunho do questionário;
- `adapteduca_questionnaire` — respostas finalizadas.

## Integração futura

Os dados fictícios ficam centralizados em `js/data.js`; autenticação e proteção de rotas ficam em `js/auth.js`; componentes e navegação ficam em arquivos separados. Assim, o `localStorage` poderá ser substituído gradualmente por APIs PHP, sessões e MySQL sem reconstruir as páginas.
