"""RF03, RF06-RF11, RF13, RF14, RF16-RF20."""
import io

import pytest

from app import create_app, db

TEXTO = (
    "A fotossíntese é o processo pelo qual as plantas produzem o próprio alimento. "
    "Entretanto, esse processo só acontece na presença de luz solar, água e gás carbônico. "
    "Durante a fotossíntese, a clorofila captura a energia da luz e a transforma em energia química. "
    "O oxigênio liberado pela fotossíntese é essencial para a vida dos animais. "
    "Portanto, as plantas são fundamentais para o equilíbrio do planeta. "
    "A glicose produzida serve de alimento para a planta e para os animais que se alimentam dela."
)


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def h(t):
    return {"Authorization": f"Bearer {t}"}


def reg(client, nome, email, perfil, **extra):
    r = client.post("/api/auth/register", json={
        "nome": nome, "email": email, "senha": "senha-segura-1", "tipoPerfil": perfil, **extra})
    assert r.status_code == 201, r.json
    return r.json["token"], r.json["dados"]


@pytest.fixture()
def cenario(client):
    """Professor (Biologia) com turma, aluno vinculado e responsável vinculado."""
    ptoken, prof = reg(client, "Prof", "p@x.com", "Professor", disciplina="Biologia")
    atoken, aluno = reg(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    rtoken, resp = reg(client, "Mae", "m@x.com", "Responsavel")
    turma = client.post("/api/turmas/", json={"codigo": "T1", "nome": "T1"}, headers=h(ptoken)).json["dados"]
    client.post(f"/api/turmas/{turma['id']}/alunos", json={"matricula": "M1"}, headers=h(ptoken))
    client.post("/api/responsaveis/me/filhos", json={"matricula": "M1", "email": "ana@x.com"}, headers=h(rtoken))
    return dict(client=client, ptoken=ptoken, atoken=atoken, rtoken=rtoken,
                turma=turma["id"], aluno=aluno["id"], resp=resp["id"])


# ── RF03 ─────────────────────────────────────────────────────────────────────
def test_recuperacao_de_senha(app, client):
    reg(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    # mesma resposta para e-mail existente e inexistente
    a = client.post("/api/auth/esqueci-senha", json={"email": "ana@x.com"})
    b = client.post("/api/auth/esqueci-senha", json={"email": "ninguem@x.com"})
    assert a.status_code == b.status_code == 200 and a.json == b.json
    outbox = app.extensions["outbox"]
    assert len(outbox) == 1 and outbox[0]["para"] == "ana@x.com"
    token = outbox[0]["corpo"].split("token=")[1].split()[0]

    assert client.post("/api/auth/redefinir-senha", json={"token": token, "senha": "curta"}).status_code == 422
    assert client.post("/api/auth/redefinir-senha", json={"token": "lixo", "senha": "nova-senha-123"}).status_code == 400
    assert client.post("/api/auth/redefinir-senha", json={"token": token, "senha": "nova-senha-123"}).status_code == 200
    assert client.post("/api/auth/login", json={"email": "ana@x.com", "senha": "nova-senha-123"}).status_code == 200
    assert client.post("/api/auth/login", json={"email": "ana@x.com", "senha": "senha-segura-1"}).status_code == 401
    # link de uso único
    assert client.post("/api/auth/redefinir-senha", json={"token": token, "senha": "outra-senha-123"}).status_code == 400


def test_token_de_reset_expirado(app, client):
    reg(client, "Ana", "ana@x.com", "Aluno", matricula="M1")
    client.post("/api/auth/esqueci-senha", json={"email": "ana@x.com"})
    token = app.extensions["outbox"][0]["corpo"].split("token=")[1].split()[0]
    app.config["RESET_TOKEN_MAX_AGE"] = -1
    r = client.post("/api/auth/redefinir-senha", json={"token": token, "senha": "nova-senha-123"})
    assert r.status_code == 400 and "expirou" in r.json["mensagem"]


# ── RF06 conteúdos ───────────────────────────────────────────────────────────
def _pdf_com_texto(texto):
    from pypdf import PdfWriter
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    for linha in texto.split(". "):
        c.drawString(40, y, linha[:110]); y -= 18
    c.save()
    return buf.getvalue()


def test_conteudo_texto_e_permissoes(cenario):
    c = cenario["client"]
    corpo = {"titulo": "Fotossíntese", "tipo": "Texto", "texto": TEXTO, "turma_id": cenario["turma"]}
    assert c.post("/api/conteudos/", json=corpo, headers=h(cenario["atoken"])).status_code == 403
    r = c.post("/api/conteudos/", json=corpo, headers=h(cenario["ptoken"]))
    assert r.status_code == 201
    cid = r.json["dados"]["id"]
    assert c.post("/api/conteudos/", json={**corpo, "texto": "curto"}, headers=h(cenario["ptoken"])).status_code == 422
    assert c.post("/api/conteudos/", json={**corpo, "tipo": "Link", "arquivo": "javascript:x"},
                  headers=h(cenario["ptoken"])).status_code == 422
    # aluno da turma vê; aluno de fora não
    assert len(c.get("/api/conteudos/", headers=h(cenario["atoken"])).json["dados"]) == 1
    assert c.get(f"/api/conteudos/{cid}", headers=h(cenario["atoken"])).json["dados"]["texto"] == TEXTO
    btoken, _ = reg(c, "Beto", "b@x.com", "Aluno", matricula="M2")
    assert c.get("/api/conteudos/", headers=h(btoken)).json["dados"] == []
    assert c.get(f"/api/conteudos/{cid}", headers=h(btoken)).status_code == 404
    assert c.get(f"/api/conteudos/{cid}/adaptacao?modo=resumo", headers=h(btoken)).status_code == 404
    # outro professor não apaga
    otoken, _ = reg(c, "Outro", "o@x.com", "Professor")
    assert c.delete(f"/api/conteudos/{cid}", headers=h(otoken)).status_code == 404
    assert c.delete(f"/api/conteudos/{cid}", headers=h(cenario["ptoken"])).status_code == 200


def test_upload_pdf_extrai_texto(cenario):
    c = cenario["client"]
    pdf = _pdf_com_texto(TEXTO)
    r = c.post("/api/conteudos/", headers=h(cenario["ptoken"]), content_type="multipart/form-data", data={
        "titulo": "PDF", "tipo": "PDF", "turma_id": cenario["turma"], "arquivo": (io.BytesIO(pdf), "aula.pdf")})
    assert r.status_code == 201, r.json
    cid = r.json["dados"]["id"]
    assert r.json["dados"]["temPdf"]
    texto = c.get(f"/api/conteudos/{cid}", headers=h(cenario["atoken"])).json["dados"]["texto"]
    assert "fotossíntese" in texto.lower()
    dl = c.get(f"/api/conteudos/{cid}/arquivo", headers=h(cenario["atoken"]))
    assert dl.status_code == 200 and dl.data.startswith(b"%PDF")
    # arquivo que não é PDF e PDF sem texto
    r = c.post("/api/conteudos/", headers=h(cenario["ptoken"]), content_type="multipart/form-data", data={
        "titulo": "X", "tipo": "PDF", "turma_id": cenario["turma"], "arquivo": (io.BytesIO(b"nao sou pdf"), "a.pdf")})
    assert r.status_code == 422
    from pypdf import PdfWriter
    w = PdfWriter(); w.add_blank_page(100, 100); buf = io.BytesIO(); w.write(buf)
    r = c.post("/api/conteudos/", headers=h(cenario["ptoken"]), content_type="multipart/form-data", data={
        "titulo": "X", "tipo": "PDF", "turma_id": cenario["turma"], "arquivo": (io.BytesIO(buf.getvalue()), "a.pdf")})
    assert r.status_code == 422 and "extrair" in r.json["mensagem"]


# ── RF07/08/09/10/13/14 adaptação ────────────────────────────────────────────
def test_modos_de_adaptacao_geram_conteudo_real(cenario):
    c = cenario["client"]
    cid = c.post("/api/conteudos/", json={"titulo": "F", "tipo": "Texto", "texto": TEXTO,
                 "turma_id": cenario["turma"]}, headers=h(cenario["ptoken"])).json["dados"]["id"]
    get = lambda modo: c.get(f"/api/conteudos/{cid}/adaptacao?modo={modo}", headers=h(cenario["atoken"]))
    res = get("resumo").json["dados"]["resultado"]
    assert 2 <= len(res["pontos"]) < 6 and all(p in TEXTO.replace("  ", " ") or p[:-1] in TEXTO for p in res["pontos"])
    simples = get("simplificado").json["dados"]["resultado"]
    assert "Entretanto" not in " ".join(simples["paragrafos"])
    tdah = get("tdah").json["dados"]["resultado"]
    assert tdah["totalBlocos"] >= 2 and all(len(b["itens"]) <= 3 and b["checkpoint"] for b in tdah["blocos"])
    tea = get("tea").json["dados"]["resultado"]
    assert tea["visaoGeral"].startswith("Este texto fala sobre") and tea["passos"] and tea["glossario"]
    mapa = get("mapa").json["dados"]["resultado"]
    assert mapa["centro"] != "Tema central" and len(mapa["ramos"]) >= 2
    audio = get("audio").json["dados"]["resultado"]
    assert audio["lang"] == "pt-BR" and audio["segmentos"] and all(len(s) < 400 for s in audio["segmentos"])
    cards = get("flashcards").json["dados"]["resultado"]["cartoes"]
    assert cards and "frente" in cards[0]
    assert get("inexistente").status_code == 422
    # segunda chamada vem do cache (mesmo resultado)
    assert get("resumo").json["dados"]["resultado"] == res


def test_personalizacao_pelo_questionario(cenario):
    c = cenario["client"]
    cid = c.post("/api/conteudos/", json={"titulo": "F", "tipo": "Texto", "texto": TEXTO,
                 "turma_id": cenario["turma"]}, headers=h(cenario["ptoken"])).json["dados"]["id"]
    para_mim = lambda: c.get(f"/api/conteudos/{cid}/adaptacao", headers=h(cenario["atoken"])).json["dados"]
    assert para_mim()["modo"] == "simplificado"  # sem questionário
    c.put("/api/alunos/me/questionario", headers=h(cenario["atoken"]), json={"respostas": {
        "formats": ["Resumos"], "necessidades": ["TDAH"], "concentracao": "Menos de 15 minutos"}})
    d = para_mim()
    assert d["modo"] == "tdah" and d["recomendado"] is True
    modos = c.get("/api/estudo/modos", headers=h(cenario["atoken"])).json["dados"]
    foco = next(m for m in modos["modos"] if m["id"] == "foco")
    assert modos["recomendado"] == "tdah" and foco["minutosFoco"] == 10


def test_adaptacao_avulsa(cenario):
    c = cenario["client"]
    r = c.post("/api/adaptar", json={"modo": "mapa", "texto": TEXTO}, headers=h(cenario["atoken"]))
    assert r.status_code == 200 and r.json["dados"]["resultado"]["ramos"]
    assert c.post("/api/adaptar", json={"modo": "resumo", "texto": "oi"}, headers=h(cenario["atoken"])).status_code == 422
    assert c.post("/api/adaptar", json={"modo": "resumo", "texto": TEXTO}).status_code == 401


# ── RF11 etapas ──────────────────────────────────────────────────────────────
def test_atividade_em_etapas(cenario):
    c = cenario["client"]
    r = c.post("/api/atividades/", headers=h(cenario["ptoken"]), json={
        "titulo": "Experimento", "turma_id": cenario["turma"],
        "etapas": "Separe os materiais: copo e feijão\nPlante o feijão: coloque no algodão\nObserve e anote"})
    assert r.status_code == 201
    etapas = r.json["dados"]["etapas"]
    assert [e["titulo"] for e in etapas] == ["Separe os materiais", "Plante o feijão", "Observe e anote"]
    aid = r.json["dados"]["id"]
    url = f"/api/atividades/{aid}/resposta"
    # progresso por etapa é salvo
    r = c.put(url, json={"etapasConcluidas": [0, 1]}, headers=h(cenario["atoken"]))
    assert r.status_code == 200 and r.json["dados"]["etapasConcluidas"] == [0, 1]
    assert c.get(f"/api/atividades/{aid}", headers=h(cenario["atoken"])).json["dados"]["minhaResposta"]["etapasConcluidas"] == [0, 1]
    # não envia com etapa faltando / etapa inexistente
    assert c.put(url, json={"enviar": True}, headers=h(cenario["atoken"])).status_code == 422
    assert c.put(url, json={"etapasConcluidas": [9]}, headers=h(cenario["atoken"])).status_code == 422
    r = c.put(url, json={"etapasConcluidas": [0, 1, 2], "enviar": True}, headers=h(cenario["atoken"]))
    assert r.status_code == 200 and r.json["dados"]["status"] == "Enviada"


# ── RF18 feedback + RF16/17/19/20 ────────────────────────────────────────────
def test_feedback_nota_progresso_relatorios(cenario):
    c, P, A, R = cenario["client"], h(cenario["ptoken"]), h(cenario["atoken"]), h(cenario["rtoken"])
    t = cenario["turma"]
    a1 = c.post("/api/atividades/", json={"titulo": "A1", "turma_id": t, "questoes": "q1"}, headers=P).json["dados"]["id"]
    a2 = c.post("/api/atividades/", json={"titulo": "A2", "turma_id": t, "prazo": "2020-01-01", "questoes": "q1"}, headers=P).json["dados"]["id"]

    # feedback/nota exigem envio; só o professor da turma
    fb = {"atividade_id": a1, "aluno_id": cenario["aluno"], "tipo": "Correcao", "mensagem": "Revise a questão 1.", "nota": 4}
    assert c.post("/api/feedbacks/", json=fb, headers=P).status_code == 422
    c.put(f"/api/atividades/{a1}/resposta", json={"respostas": ["x"], "enviar": True}, headers=A)
    assert c.post("/api/feedbacks/", json=fb, headers=A).status_code == 403
    otoken, _ = reg(c, "Outro", "o@x.com", "Professor")
    assert c.post("/api/feedbacks/", json=fb, headers=h(otoken)).status_code == 403
    assert c.post("/api/feedbacks/", json={**fb, "nota": 11}, headers=P).status_code == 422
    assert c.post("/api/feedbacks/", json={**fb, "mensagem": " "}, headers=P).status_code == 422
    assert c.post("/api/feedbacks/", json=fb, headers=P).status_code == 201

    # aluno e responsável veem; aluno de fora não
    assert [f["mensagem"] for f in c.get("/api/feedbacks/", headers=A).json["dados"]] == ["Revise a questão 1."]
    assert len(c.get("/api/feedbacks/", headers=R).json["dados"]) == 1
    btoken, _ = reg(c, "Beto", "b@x.com", "Aluno", matricula="M2")
    assert c.get("/api/feedbacks/", headers=h(btoken)).json["dados"] == []
    ativ = c.get("/api/atividades/", headers=A).json["dados"]
    a1d = next(x for x in ativ if x["id"] == a1)
    assert a1d["nota"] == 4 and a1d["feedbacks"][0]["tipo"] == "Correcao"
    resp_prof = c.get(f"/api/atividades/{a1}/respostas", headers=P).json["dados"][0]
    assert resp_prof["nota"] == 4 and len(resp_prof["feedbacks"]) == 1

    # sessões de estudo
    assert c.post("/api/estudo/sessoes", json={"modo": "foco", "segundos": 1200}, headers=A).status_code == 201
    assert c.post("/api/estudo/sessoes", json={"modo": "foco", "segundos": 1}, headers=A).status_code == 422
    assert c.post("/api/estudo/sessoes", json={"modo": "x", "segundos": 600}, headers=A).status_code == 422
    assert c.post("/api/estudo/sessoes", json={"modo": "foco", "segundos": 600}, headers=P).status_code == 403

    # RF16: progresso real do aluno
    d = c.get(f"/api/progresso/aluno/{cenario['aluno']}", headers=A).json["dados"]
    assert d["progresso"] == 50.0 and d["atividades"] == {"total": 2, "enviadas": 1, "pendentes": 1, "atrasadas": 1}
    assert d["mediaNota"] == 4 and d["desempenho"] == 40 and d["status"] == "Precisa de atenção"
    assert d["tempoEstudoMinutos"] == 20 and d["tempoPorModo"] == {"foco": 20}
    assert d["materias"][0]["materia"] == "Biologia" and "Biologia" in d["materiasDificeis"]
    assert sum(w["atividadesEnviadas"] for w in d["evolucao"]) == 1
    # permissões
    assert c.get(f"/api/progresso/aluno/{cenario['aluno']}", headers=R).status_code == 200
    assert c.get(f"/api/progresso/aluno/{cenario['aluno']}", headers=P).status_code == 200
    assert c.get(f"/api/progresso/aluno/{cenario['aluno']}", headers=h(btoken)).status_code == 404
    assert c.get(f"/api/progresso/aluno/{cenario['aluno']}", headers=h(otoken)).status_code == 404

    # RF17: professor
    dp = c.get("/api/progresso/professor", headers=P).json["dados"]
    assert dp["totalAlunos"] == 1 and dp["alunosEmAtencao"][0]["nome"] == "Ana"
    assert c.get("/api/progresso/professor", headers=A).status_code == 403

    # RF19: responsável só vê o filho vinculado
    dr = c.get("/api/progresso/responsavel", headers=R).json["dados"]
    assert dr["totalFilhos"] == 1 and dr["filhos"][0]["aluno"]["nome"] == "Ana"
    rtoken2, _ = reg(c, "Tio", "t@x.com", "Responsavel")
    assert c.get("/api/progresso/responsavel", headers=h(rtoken2)).json["dados"]["totalFilhos"] == 0
    assert c.get(f"/api/progresso/aluno/{cenario['aluno']}", headers=h(rtoken2)).status_code == 404

    # RF20: relatório salvo e consultável
    rel = c.post(f"/api/relatorios/aluno/{cenario['aluno']}", json={"dias": 60}, headers=P)
    assert rel.status_code == 201 and rel.json["dados"]["periodo"] == "Últimos 60 dias"
    rid = rel.json["dados"]["id"]
    assert c.get(f"/api/relatorios/{rid}", headers=R).json["dados"]["relatorio"]["progresso"] == 50.0
    assert len(c.get(f"/api/relatorios/aluno/{cenario['aluno']}", headers=A).json["dados"]) == 1
    assert c.get(f"/api/relatorios/{rid}", headers=h(btoken)).status_code == 404
    assert c.post(f"/api/relatorios/aluno/{cenario['aluno']}", json={"dias": "x"}, headers=P).status_code == 422
