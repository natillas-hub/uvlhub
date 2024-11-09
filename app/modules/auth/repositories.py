from app.modules.auth.models import User
from core.repositories.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create(self, commit: bool = True, **kwargs):
        password = kwargs.pop("password")
        instance = self.model(**kwargs)
        instance.set_password(password)
        self.session.add(instance)
        if commit:
            self.session.commit()
        else:
            self.session.flush()
        return instance

    def get_by_email(self, email: str):
        return self.model.query.filter_by(email=email).first()

    def check_security_answers(self, user: User, answer1: str, answer2: str, answer3: str) -> bool:
        return (user.check_security_answer1(answer1) and
                user.check_security_answer2(answer2) and
                user.check_security_answer3(answer3))

    def update_password(self, user: User, new_password: str):
        user.set_password(new_password)
        self.session.commit()
