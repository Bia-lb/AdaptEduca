from werkzeug.security import check_password_hash, generate_password_hash
from repositories.usuario_repository import usuario_repository
from services.base_service import BaseService


class UsuarioService(BaseService):
    def __init__(self):
        super().__init__(usuario_repository, ["nome", "email", "senha", "tipoPerfil"], ["nome", "email", "senha", "tipoPerfil"])

    def criar(self, dados):
        dados = self.preparar_dados(dados, True)
        dados["email"] = dados["email"].strip().lower()
        if usuario_repository.buscar_por_email(dados["email"]):
            raise ValueError("Já existe uma conta com este e-mail.")
        dados["senha"] = generate_password_hash(dados["senha"])
        return usuario_repository.criar(dados)

    def atualizar(self, identificador, dados):
        registro = self.buscar(identificador)
        dados = self.preparar_dados(dados)
        if "email" in dados:
            dados["email"] = dados["email"].strip().lower()
            existente = usuario_repository.buscar_por_email(dados["email"])
            if existente and existente.id != registro.id:
                raise ValueError("Já existe uma conta com este e-mail.")
        if dados.get("senha"):
            dados["senha"] = generate_password_hash(dados["senha"])
        else:
            dados.pop("senha", None)
        return usuario_repository.atualizar(registro, dados)

    def autenticar(self, email, senha):
        usuario = usuario_repository.buscar_por_email(email.strip().lower())
        if not usuario or not check_password_hash(usuario.senha, senha):
            raise ValueError("E-mail ou senha inválidos.")
        return usuario


usuario_service = UsuarioService()
