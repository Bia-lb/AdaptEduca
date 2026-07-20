from datetime import date


class BaseService:
    def __init__(self, repository, campos, obrigatorios=(), campos_data=()):
        self.repository = repository
        self.campos = set(campos)
        self.obrigatorios = set(obrigatorios)
        self.campos_data = set(campos_data)

    def listar(self):
        return self.repository.listar()

    def buscar(self, identificador):
        registro = self.repository.buscar(identificador)
        if not registro:
            raise LookupError("Registro não encontrado.")
        return registro

    def preparar_dados(self, dados, criacao=False):
        dados_filtrados = {campo: valor for campo, valor in dados.items() if campo in self.campos}
        if criacao:
            ausentes = [campo for campo in self.obrigatorios if dados_filtrados.get(campo) in (None, "")]
            if ausentes:
                raise ValueError("Campos obrigatórios: " + ", ".join(sorted(ausentes)))
        for campo in self.campos_data:
            valor = dados_filtrados.get(campo)
            if isinstance(valor, str) and valor:
                dados_filtrados[campo] = date.fromisoformat(valor)
        return dados_filtrados

    def criar(self, dados):
        return self.repository.criar(self.preparar_dados(dados, True))

    def atualizar(self, identificador, dados):
        registro = self.buscar(identificador)
        return self.repository.atualizar(registro, self.preparar_dados(dados))

    def excluir(self, identificador):
        registro = self.buscar(identificador)
        self.repository.excluir(registro)
