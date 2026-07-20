from repositories.feedback_repository import feedback_repository
from services.base_service import BaseService


class FeedbackService(BaseService):
    def __init__(self):
        super().__init__(feedback_repository, ['atividade_id', 'mensagem', 'data', 'tipo'], ['mensagem'], ['data'])


feedback_service = FeedbackService()
