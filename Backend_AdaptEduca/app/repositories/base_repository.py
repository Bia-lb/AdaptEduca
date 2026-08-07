from typing import Generic, TypeVar, Type, Optional, List
from app import db

T = TypeVar("T", bound=db.Model)


class BaseRepository(Generic[T]):
    """
    Repositório genérico. Cada repositório concreto herda desta classe
    e só precisa sobrescrever métodos com lógica específica da entidade.
    Princípio SRP: toda operação de persistência fica aqui.
    """

    def __init__(self, model: Type[T]) -> None:
        self._model = model

    def listar_todos(self) -> List[T]:
        return self._model.query.all()

    def buscar_por_id(self, id: int) -> Optional[T]:
        return self._model.query.get(id)

    def salvar(self, entidade: T) -> T:
        db.session.add(entidade)
        db.session.commit()
        db.session.refresh(entidade)
        return entidade

    def deletar(self, entidade: T) -> None:
        db.session.delete(entidade)
        db.session.commit()
