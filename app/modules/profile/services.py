from app.modules.profile.repositories import UserProfileRepository
from core.services.BaseService import BaseService
from app.modules.auth.repositories import UserRepository


class UserProfileService(BaseService):
    def __init__(self):
        super().__init__(UserProfileRepository())

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None

        return None, form.errors


class AnswersUpdateService:
    def __init__(self):
        self.user_repository = UserRepository()

    def change_answers(self, user, new_answer1, new_answer2, new_answer3):
        self.user_repository.update_answers(user, new_answer1, new_answer2, new_answer3)
        return "Security answers updated successfully."
