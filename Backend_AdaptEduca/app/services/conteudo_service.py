import json
import os
import re
import uuid
from datetime import date
from io import BytesIO
from typing import List, Optional

from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.models.adaptacao import Adaptacao
from app.models.aluno import Aluno
from app.models.conteudo import Conteudo
from app.models.turma import Turma
from app.services import adaptacao_engine as motor
from app.services import ia_adaptacao
from app.services.turma_service import TurmaService

TIPOS = ("Texto", "PDF", "Link", "Video")
MAX_PDF = 10 * 1024 * 1024


def extrair_texto_pdf(dados: bytes) -> str:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError
    if not dados.startswith(b"%PDF"):
        raise ValueError("O arquivo enviado não é um PDF válido.")
    try:
        leitor = PdfReader(BytesIO(dados))
        if leitor.is_encrypted:
            raise ValueError("O PDF está protegido por senha.")
        texto = "\n\n".join((pagina.extract_text() or "") for pagina in leitor.pages)
    except (PdfReadError, KeyError, ValueError) as exc:
        if isinstance(exc, ValueError) and "senha" in str(exc):
            raise
        raise ValueError("Não foi possível ler o PDF.")
    texto = motor.limpar(texto)
    if len(texto) < 40:
        raise ValueError("Não foi possível extrair texto do PDF (pode ser um PDF escaneado como imagem).")
    return texto


class ConteudoService:
    def __init__(self) -> None:
        self._turmas = TurmaService()

    def listar_para(self, usuario_id: int, perfil: str) -> List[dict]:
        turmas = self._turmas.listar_para(usuario_id, perfil)
        nomes = {t.id: t.nome for t in turmas}
        if not nomes:
            return []
        itens = (Conteudo.query.filter(Conteudo.turma_id.in_(nomes))
                 .order_by(Conteudo.dataPostagem.desc(), Conteudo.id.desc()).all())
        saida = []
        for c in itens:
            d = c.to_dict()
            d["turmaNome"] = nomes[c.turma_id]
            d["temTexto"] = bool(c.texto)
            saida.append(d)
        return saida

    def buscar_visivel(self, id: int, usuario_id: int, perfil: str) -> Optional[Conteudo]:
        c = db.session.get(Conteudo, id)
        if c and self._turmas.tem_acesso(c.turma, usuario_id, perfil):
            return c
        return None

  
    # ==========================================
    # PUBLICAR CONTEÚDO
    # ==========================================

    def criar(self, dados: dict, arquivo, professor_id: int) -> Conteudo:

        # Verificar a turma.
        try:
            turma = db.session.get(
                Turma,
                int(dados.get("turma_id"))
            )
        except (TypeError, ValueError):
            turma = None

        if not turma or turma.professor_id != professor_id:
            raise PermissionError(
                "Você só pode publicar conteúdo nas suas turmas."
            )

        # Verificar o título.
        titulo = (dados.get("titulo") or "").strip()

        if not titulo:
            raise ValueError("O título é obrigatório.")

        # ======================================
        # RECEBER TEXTO, PDF E LINK
        # ======================================

        texto_digitado = motor.limpar(
            dados.get("texto") or ""
        )

        link = (
            dados.get("linkExterno") or ""
        ).strip()

        # Compatibilidade com publicações antigas.
        if not link and dados.get("tipo") in ("Link", "Video"):
            link = (dados.get("arquivo") or "").strip()

        tem_pdf = bool(
            arquivo and arquivo.filename
        )

        if not (texto_digitado or link or tem_pdf):
            raise ValueError(
                "Adicione texto, PDF ou link antes de publicar."
            )

        # Validar o link.
        if link and (
            len(link) > 2048
            or not re.match(r"^https?://[^\s]+$", link, re.I)
        ):
            raise ValueError(
                "Informe um link HTTP/HTTPS válido."
            )

        nome_arquivo = None
        original = None
        texto_pdf = ""

        # ======================================
        # PROCESSAR PDF
        # ======================================

        if tem_pdf:

            conteudo_bytes = arquivo.read(MAX_PDF + 1)

            if len(conteudo_bytes) > MAX_PDF:
                raise ValueError(
                    "O PDF deve ter no máximo 10 MB."
                )

            # Extrair o texto para adaptação.
            texto_pdf = extrair_texto_pdf(
                conteudo_bytes
            )

            pasta = current_app.config["UPLOAD_DIR"]

            os.makedirs(
                pasta,
                exist_ok=True
            )

            # Nome único para evitar conflitos.
            nome_arquivo = f"{uuid.uuid4().hex}.pdf"

            caminho = os.path.join(
                pasta,
                nome_arquivo
            )

            with open(caminho, "wb") as f:
                f.write(conteudo_bytes)

            original = secure_filename(
                arquivo.filename or "conteudo.pdf"
            )[:255]

        # ======================================
        # DEFINIR TIPO PRINCIPAL
        # ======================================

        # Preserva compatibilidade com o Enum
        # existente no banco de dados.
        tipo = (
            "PDF"
            if tem_pdf
            else "Texto"
            if texto_digitado
            else "Link"
        )

        # Combina texto digitado e extraído.
        texto_final = "\n\n".join(
            parte
            for parte in (
                texto_digitado,
                texto_pdf
            )
            if parte
        ) or None

        # ======================================
        # CRIAR REGISTRO NO MYSQL
        # ======================================

        conteudo = Conteudo(
            titulo=titulo,
            tipo=tipo,
            arquivo=nome_arquivo,
            arquivoOriginal=original,
            linkExterno=link or None,
            texto=texto_final,
            dataPostagem=date.today(),
            turma_id=turma.id
        )

        try:

            db.session.add(conteudo)
            db.session.commit()

        except Exception:

            db.session.rollback()

            # Remove o PDF se o banco falhar.
            if nome_arquivo:
                try:
                    os.remove(
                        os.path.join(
                            current_app.config["UPLOAD_DIR"],
                            nome_arquivo
                        )
                    )
                except OSError:
                    pass

            raise

        return conteudo


    
    def caminho_pdf(self, conteudo: Conteudo) -> Optional[str]:

        if (
            not conteudo.arquivo
            or not conteudo.arquivo.lower().endswith(".pdf")
        ):
            return None

        caminho = os.path.join(
            current_app.config["UPLOAD_DIR"],
            os.path.basename(conteudo.arquivo)
        )

        return caminho if os.path.exists(caminho) else None


    def deletar(self, conteudo: Conteudo) -> None:
        caminho = self.caminho_pdf(conteudo)
        for a in list(conteudo.adaptacoes):
            db.session.delete(a)
        db.session.delete(conteudo)
        db.session.commit()
        if caminho:
            try:
                os.remove(caminho)
            except OSError:
                pass


    @staticmethod
    def dividir_em_partes(texto: str, tamanho: int = 10000) -> list[str]:
        """Divide textos longos em partes menores."""

        partes = []
        atual = []
        quantidade = 0

        for trecho in re.findall(r"\S+\s*", texto):

            if len(trecho) > tamanho:
                if atual:
                    partes.append("".join(atual).strip())
                    atual = []
                    quantidade = 0

                partes.extend(
                    trecho[i:i + tamanho]
                    for i in range(0, len(trecho), tamanho)
                )
                continue

            if atual and quantidade + len(trecho) > tamanho:
                partes.append("".join(atual).strip())
                atual = []
                quantidade = 0

            atual.append(trecho)
            quantidade += len(trecho)

        if atual:
            partes.append("".join(atual).strip())

        return partes


    # ── adaptação (RF07/08/09/10/13) ────────────────────────────────────────
   
    # ── adaptação (RF07/08/09/10/13) ───────────────────

    def adaptar(
        self,
        conteudo: Conteudo,
        modo: str,
        aluno: Optional[Aluno] = None,
        usuario_id: Optional[int] = None,
        parte: int = 1
    ) -> dict:

        recomendado = False

        # Escolher o modo recomendado para o aluno
        if modo in ("para-mim", "", None):
            quest = aluno.respostas_questionario() if aluno else {}
            modo, recomendado = motor.modo_recomendado(quest), True

        # Validar o modo selecionado
        if modo not in motor.MODOS:
            raise ValueError(
                f"Modo inválido. Use: {', '.join(motor.MODOS)}."
            )

        if not conteudo.texto:
            raise ValueError(
                "Este conteúdo não tem texto para adaptar."
            )

        # Dividir PDFs e textos muito longos
        longo = len(conteudo.texto) > motor.MAX_CARACTERES

        if longo:
            partes = self.dividir_em_partes(
                conteudo.texto,
                tamanho=10000
            )
        else:
            partes = [conteudo.texto]

        # Verificar se a parte solicitada existe
        if parte < 1 or parte > len(partes):
            raise ValueError(
                f"Parte inválida. Escolha entre 1 e {len(partes)}."
            )

        texto_parte = partes[parte - 1]
        rotulo = motor.MODOS[modo][0]

        # Para documentos longos, evitar reutilizar
        # uma adaptação salva para outra parte do PDF.
        if longo:
            salvo = None
        else:
            salvo = Adaptacao.query.filter_by(
                conteudo_id=conteudo.id,
                modo=rotulo
            ).first()

        resultado = None

        if salvo and salvo.resultado:
            resultado = json.loads(salvo.resultado)

        # Tentar melhorar um resultado por regras com IA
        melhorar = (
            resultado is not None
            and resultado.get("fonte") != "ia"
            and ia_adaptacao.pode_usar(modo, texto_parte)
        )

        if resultado is None or melhorar:

            # Enviar apenas a parte atual para a IA
            resultado = ia_adaptacao.adaptar_com_fallback(
                usuario_id,
                modo,
                texto_parte
            )

            # Manter o salvamento para conteúdos menores
            if not longo:

                texto_json = json.dumps(
                    resultado,
                    ensure_ascii=False
                )

                if salvo:
                    salvo.resultado = texto_json
                else:
                    db.session.add(
                        Adaptacao(
                            conteudo_id=conteudo.id,
                            modo=rotulo,
                            resultado=texto_json,
                            audio=(modo == "audio"),
                            mapaMental=(modo == "mapa")
                        )
                    )

                db.session.commit()

        return {
            "conteudo_id": conteudo.id,
            "modo": modo,
            "recomendado": recomendado,
            "resultado": resultado,
            "parte": parte,
            "totalPartes": len(partes)
        }
