"""Fluxo central: cadastro/login -> questionário -> turma -> atividade -> resposta."""
import pytest

from app import create_app, db
from app.models.usuario import Usuario


@pytest.fixture()
def client():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def registrar(client, nome, email, perfil, **extra):
    r = client.post("/api/auth/register", json={
        "nome": nome, "email": email, "senha": "senha-segura-1", "tipoPerfil": perfil, **extra})
    assert r.status_code == 201, r.json
    return r.json["token"], r.json["dados"]


def h(token):
    return {"Authorization": f"Bearer {token}"}


def test_senha_gravada_como_hash_e_login(client):
    registrar(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    assert Usuario.query.filter_by(email="ana@x.com").one().senha.startswith("pbkdf2:")
    ok = client.post("/api/auth/login", json={"email": "ANA@x.com", "senha": "senha-segura-1"})
    assert ok.status_code == 200 and ok.json["token"]
    assert "senha" not in ok.json["dados"]
    assert client.post("/api/auth/login", json={"email": "ana@x.com", "senha": "errada"}).status_code == 401


def test_senha_legada_em_texto_puro_migra_no_login(client):
    db.session.execute(db.text(
        "INSERT INTO usuario (nome,email,senha,tipoPerfil) VALUES ('Leg','leg@x.com','senha123','Professor')"))
    db.session.execute(db.text("INSERT INTO professor (id) SELECT id FROM usuario WHERE email='leg@x.com'"))
    db.session.commit()
    assert client.post("/api/auth/login", json={"email": "leg@x.com", "senha": "senha123"}).status_code == 200
    db.session.expire_all()
    assert Usuario.query.filter_by(email="leg@x.com").one().senha.startswith("pbkdf2:")


def test_senha_curta_e_email_duplicado_rejeitados(client):
    r = client.post("/api/auth/register", json={
        "nome": "A", "email": "a@x.com", "senha": "123", "tipoPerfil": "Aluno"})
    assert r.status_code == 422
    registrar(client, "A", "a@x.com", "Aluno")
    r = client.post("/api/auth/register", json={
        "nome": "B", "email": "a@x.com", "senha": "senha-segura-1", "tipoPerfil": "Professor"})
    assert r.status_code == 409


def test_rotas_exigem_token(client):
    for caminho in ("/api/turmas/", "/api/atividades/", "/api/alunos/", "/api/usuarios/"):
        assert client.get(caminho).status_code == 401
    assert client.get("/api/turmas/", headers=h("token-invalido")).status_code == 401


def test_questionario_salvo_no_banco(client):
    token, _ = registrar(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    respostas = {"formats": ["Vídeos", "Mapas Mentais"], "necessidades": ["TDAH"], "horario": "Manhã"}
    r = client.put("/api/alunos/me/questionario", json={"respostas": respostas}, headers=h(token))
    assert r.status_code == 200 and r.json["dados"]["questionarioConcluido"] is True
    assert r.json["dados"]["preferenciaAprendizagem"] == "Vídeos, Mapas Mentais"
    me = client.get("/api/alunos/me", headers=h(token)).json["dados"]
    assert me["questionario"]["necessidades"] == ["TDAH"]
    login = client.post("/api/auth/login", json={"email": "ana@x.com", "senha": "senha-segura-1"})
    assert login.json["dados"]["questionarioConcluido"] is True
    assert client.put("/api/alunos/me/questionario", json={"respostas": {"formats": []}},
                      headers=h(token)).status_code == 422


def test_questionario_nao_vaza_para_professor(client):
    ptoken, _ = registrar(client, "Prof", "p@x.com", "Professor")
    atoken, aluno = registrar(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    client.put("/api/alunos/me/questionario",
               json={"respostas": {"formats": ["Áudios"], "necessidades": ["TEA"]}}, headers=h(atoken))
    dados = client.get(f"/api/alunos/{aluno['id']}", headers=h(ptoken)).json["dados"]
    assert "questionario" not in dados and "TEA" not in str(dados)
    assert client.get("/api/alunos/me", headers=h(ptoken)).status_code == 403


def test_fluxo_turma_atividade_resposta(client):
    ptoken, prof = registrar(client, "Prof", "p@x.com", "Professor")
    outro_token, _ = registrar(client, "Outro", "o@x.com", "Professor")
    atoken, aluno = registrar(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    btoken, _ = registrar(client, "Beto", "b@x.com", "Aluno", matricula="M2")

    # aluno não cria turma
    assert client.post("/api/turmas/", json={"codigo": "9A", "nome": "9A"}, headers=h(atoken)).status_code == 403
    # professor cria turma; professor_id vem do token, não do corpo
    r = client.post("/api/turmas/", json={"codigo": "9A", "nome": "9º A", "professor_id": 999}, headers=h(ptoken))
    assert r.status_code == 201 and r.json["dados"]["professor_id"] == prof["id"]
    turma_id = r.json["dados"]["id"]
    assert client.post("/api/turmas/", json={"codigo": "9A", "nome": "x"}, headers=h(ptoken)).status_code == 409

    # vínculo por matrícula
    r = client.post(f"/api/turmas/{turma_id}/alunos", json={"matricula": "M1"}, headers=h(ptoken))
    assert r.status_code == 201
    assert client.post(f"/api/turmas/{turma_id}/alunos", json={"matricula": "M1"}, headers=h(ptoken)).status_code == 409
    assert client.post(f"/api/turmas/{turma_id}/alunos", json={"matricula": "ZZ"}, headers=h(ptoken)).status_code == 404
    assert client.post(f"/api/turmas/{turma_id}/alunos", json={"matricula": "M2"}, headers=h(outro_token)).status_code == 403

    # cada perfil só vê o que é seu
    assert len(client.get("/api/turmas/", headers=h(atoken)).json["dados"]) == 1
    assert client.get("/api/turmas/", headers=h(btoken)).json["dados"] == []
    assert client.get("/api/turmas/", headers=h(outro_token)).json["dados"] == []

    # atividade com prazo e questões
    corpo = {"titulo": "Lista 1", "turma_id": turma_id, "prazo": "2026-12-01",
             "questoes": "Quanto é 2+2?\nQuanto é 3+3?"}
    assert client.post("/api/atividades/", json=corpo, headers=h(outro_token)).status_code == 403
    assert client.post("/api/atividades/", json={**corpo, "prazo": "01/12"}, headers=h(ptoken)).status_code == 422
    r = client.post("/api/atividades/", json=corpo, headers=h(ptoken))
    assert r.status_code == 201 and r.json["dados"]["questoes"] == ["Quanto é 2+2?", "Quanto é 3+3?"]
    aid = r.json["dados"]["id"]

    lista = client.get("/api/atividades/", headers=h(atoken)).json["dados"]
    assert len(lista) == 1 and lista[0]["status"] == "Pendente"
    assert client.get("/api/atividades/", headers=h(btoken)).json["dados"] == []
    assert client.get(f"/api/atividades/{aid}", headers=h(btoken)).status_code == 404

    # aluno de fora não responde; aluno da turma salva rascunho e envia
    assert client.put(f"/api/atividades/{aid}/resposta", json={"respostas": ["4", "6"], "enviar": True},
                      headers=h(btoken)).status_code == 404
    r = client.put(f"/api/atividades/{aid}/resposta", json={"respostas": ["4", ""]}, headers=h(atoken))
    assert r.status_code == 200 and r.json["dados"]["status"] == "Em andamento"
    r = client.put(f"/api/atividades/{aid}/resposta", json={"respostas": ["4", ""], "enviar": True}, headers=h(atoken))
    assert r.status_code == 422  # questão em branco
    r = client.put(f"/api/atividades/{aid}/resposta", json={"respostas": ["4", "6"], "enviar": True}, headers=h(atoken))
    assert r.status_code == 200 and r.json["dados"]["status"] == "Enviada"
    r = client.put(f"/api/atividades/{aid}/resposta", json={"respostas": ["9", "9"]}, headers=h(atoken))
    assert r.status_code == 422  # já enviada

    # progresso real, status por aluno e visão do professor
    assert client.get("/api/atividades/", headers=h(atoken)).json["dados"][0]["status"] == "Concluida"
    assert client.get("/api/alunos/me", headers=h(atoken)).json["dados"]["progresso"] == 100.0
    ativ_prof = client.get("/api/atividades/", headers=h(ptoken)).json["dados"][0]
    assert (ativ_prof["totalAlunos"], ativ_prof["totalEnviadas"]) == (1, 1)
    rs = client.get(f"/api/atividades/{aid}/respostas", headers=h(ptoken)).json["dados"]
    assert rs[0]["aluno"] == "Ana" and rs[0]["respostas"] == ["4", "6"]
    assert client.get(f"/api/atividades/{aid}/respostas", headers=h(atoken)).status_code == 403


def test_mass_assignment_bloqueado(client):
    atoken, aluno = registrar(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    r = client.put(f"/api/alunos/{aluno['id']}", headers=h(atoken),
                   json={"progresso": 100, "tipoPerfil": "Professor", "matricula": "HACK", "nome": "Ana B"})
    assert r.status_code == 200
    dados = client.get("/api/alunos/me", headers=h(atoken)).json["dados"]
    assert dados["progresso"] == 0 and dados["tipoPerfil"] == "Aluno" and dados["matricula"] == "M1"
    assert dados["nome"] == "Ana B"
    # aluno não altera outro aluno
    btoken, outro = registrar(client, "Beto", "b@x.com", "Aluno", matricula="M2")
    assert client.put(f"/api/alunos/{aluno['id']}", headers=h(btoken), json={"nome": "x"}).status_code == 403
    # troca de senha continua gravando hash
    client.put(f"/api/usuarios/{aluno['id']}", headers=h(atoken), json={"senha": "nova-senha-123"})
    assert client.post("/api/auth/login", json={"email": "ana@x.com", "senha": "nova-senha-123"}).status_code == 200


def test_dashboard_responsavel_usa_respostas_reais(client):
    ptoken, _ = registrar(client, "Prof", "p@x.com", "Professor")
    atoken, _ = registrar(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    rtoken, resp = registrar(client, "Mae", "m@x.com", "Responsavel")
    turma = client.post("/api/turmas/", json={"codigo": "T", "nome": "T"}, headers=h(ptoken)).json["dados"]
    client.post(f"/api/turmas/{turma['id']}/alunos", json={"matricula": "M1"}, headers=h(ptoken))
    assert client.post("/api/responsaveis/me/filhos", json={"matricula": "M1", "email": "outro@x.com"},
                       headers=h(rtoken)).status_code == 404  # exige matrícula E e-mail corretos
    assert client.post("/api/responsaveis/me/filhos", json={"matricula": "M1", "email": "ana@x.com"},
                       headers=h(rtoken)).status_code == 201
    a = client.post("/api/atividades/", json={"titulo": "A", "turma_id": turma["id"]}, headers=h(ptoken)).json["dados"]
    client.post("/api/atividades/", json={"titulo": "B", "turma_id": turma["id"]}, headers=h(ptoken))
    client.put(f"/api/atividades/{a['id']}/resposta", json={"respostas": [], "enviar": True}, headers=h(atoken))
    d = client.get(f"/responsavel/api/{resp['id']}/dashboard", headers=h(rtoken)).json["dados"]
    assert d["alunos"][0]["atividadesConcluidas"] == 1 and d["alunos"][0]["emAndamento"] == 1
    assert d["progressoMedio"] == 50.0
    assert client.get(f"/responsavel/api/{resp['id']}/dashboard", headers=h(atoken)).status_code == 403
