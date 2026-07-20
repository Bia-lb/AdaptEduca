from models.feedback import Feedback
from repositories.base_repository import BaseRepository


class FeedbackRepository(BaseRepository):
    def __init__(self):
        super().__init__(Feedback)


feedback_repository = FeedbackRepository()
