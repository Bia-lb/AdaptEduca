[README.md](https://github.com/user-attachments/files/30683016/README.md)
Nome do projeto: AdaptEduca

Nome completo dos integrantes da equipe:

 Arthur Vinicius Gomes Campos
 
 Bianca Alves da Silva
 
 Carlos Henrique Simoes Neto
 
 Maria Clara de Aquino Souza
 
 Maria Edurada Oliveira Lavorato Andrada
 
 Sarah Elise Alcantara de Freitas


Stack utilizada no projeto, separando frontend, backend e banco de dados:

-Frontend: HTML5, CSS e JavaScript, utilizados para desenvolver a interface do usuário.
-Backend: Python, responsável pela lógica de negócio, processamento das requisições e integração com o banco de dados.
-Banco de Dados: MySql, utilizado para armazenar e gerenciar os dados da aplicação.

Breve descrição do sistema:
O Adapt Educa é uma plataforma web desenvolvida para auxiliar estudantes com dificuldades de aprendizagem, seus responsáveis e professores. O sistema utiliza inteligência artificial para adaptar os conteúdos enviados pelos professores de acordo com o perfil e as necessidades individuais de cada aluno, tornando o processo de ensino mais acessível, personalizado e eficiente.

Os professores podem cadastrar conteúdos e acompanhar o desempenho dos alunos, enquanto os responsáveis têm acesso à evolução da aprendizagem. Já os alunos recebem materiais adaptados em diferentes formatos, como resumos, mapas mentais, textos simplificados, flashcards e outros recursos que facilitam a compreensão do conteúdo.

O objetivo do Adapt Educa é promover uma educação mais inclusiva, oferecendo ferramentas que contribuam para o desenv

Instruções básicas para executar o projeto, quando aplicável:
Instruções Básicas para Execução
Requisitos
MySQL 8.0 ou superior
Servidor web compatível com a aplicação (quando implementada)
Navegador atualizado (Google Chrome, Microsoft Edge ou Mozilla Firefox)
Conexão com a internet (caso a aplicação utilize serviços de inteligência artificial)
Configuração do Banco de Dados
Instale o MySQL.
Crie um banco de dados chamado adapt_educa.
Execute o script SQL fornecido para criar todas as tabelas e seus relacionamentos.
Verifique se todas as tabelas foram criadas corretamente antes de iniciar a aplicação.
Execução da Aplicação
Clone ou faça o download do projeto.
Configure o arquivo de conexão com o banco de dados utilizando as credenciais do seu servidor MySQL.
Inicie o servidor da aplicação conforme a tecnologia utilizada no desenvolvimento.
Acesse o sistema pelo navegador utilizando o endereço configurado (por exemplo, http://localhost).
Observações
Certifique-se de que o banco de dados esteja em execução antes de iniciar a aplicação.
Caso o sistema utilize serviços de inteligência artificial, configure as chaves de API necessárias antes da execução.
Recomenda-se utilizar versões atualizadas das dependências do projeto para garantir compatibilidade e segurança.

## Atualização: agentes de IA (Claude)

Três agentes usam a API da Anthropic. **Tudo é opcional**: sem `ANTHROPIC_API_KEY` o sistema funciona como antes (motor por regras) e os recursos de IA ficam ocultos.

1. **Adaptação de conteúdo** (`ia_adaptacao.py`): gera resumo, texto simplificado, TDAH, TEA, mapa mental e flashcards no mesmo JSON do motor por regras. A resposta é validada campo a campo; se a IA falhar, estourar a cota ou estiver fora do ar, o motor por regras assume (`fonte: "regras"`). O resultado em cache é compartilhado por conteúdo+modo e é refeito com IA quando ela ficar disponível. O modo Áudio nunca usa IA.
2. **Tutor** (`POST /api/tutor/mensagem`): chat socrático sobre um conteúdo da turma ou texto colado. A conversa vive só no navegador; o servidor não grava nada.
3. **Acompanhamento** (`POST /api/progresso/aluno/<id>/analise`): agente com ferramentas (progresso, matérias, evolução, pendências, feedbacks, modos de estudo) que escreve `resumo`, `pontosFortes`, `pontosDeAtencao` e `sugestoes` para professor, responsável ou aluno, com tom adequado a cada um. Só roda ao clicar em "Gerar análise com IA".

Configuração (variáveis de ambiente, ver `.env.example`): `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` (padrão `claude-sonnet-5-5`), `IA_LIMITE_DIARIO` (chamadas por usuário/dia), `IA_TIMEOUT`. A chave fica só no servidor. Banco: rode `Backend_AdaptEduca/migracao_v4.sql` (tabela `ia_uso`). `GET /api/ia/status` informa se a IA está disponível e quantos usos restam.

Segurança e privacidade:
- Nome, e-mail e matrícula nunca vão ao modelo; o tutor só recebe o texto do conteúdo e preferências genéricas de aprendizagem.
- Conteúdo e feedbacks entram como dados delimitados; instruções dentro deles são ignoradas. As ferramentas do agente de acompanhamento são presas ao aluno já autorizado pela rota e o modelo não escolhe o aluno.
- Cota diária por usuário, timeout, pausa de 45 s após falha da API e limite de 12 mil caracteres por conteúdo (acima disso usa regras).
- **LGPD:** os textos e dados de desempenho de menores são enviados a um terceiro (Anthropic). Antes de ativar em produção, obtenha o consentimento dos responsáveis, atualize a política de privacidade e confirme os termos de retenção de dados da API com a Anthropic.

Testes: `tests/test_agentes_ia.py` usa um cliente Claude falso (nenhuma chamada real).
