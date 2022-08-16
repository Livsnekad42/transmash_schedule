from typing import Union

from authentication.models import User


class ValidUserPasswordMixin:
    def get_valid_password(self, password: str, email: str = None, phone: str = None) -> Union[User, None]:
        user = None

        if phone:
            try:
                user = User.model_objects.filter(phone=phone).select_related("profile").\
                    select_related("profile__company", "profile__manager").get()

            except User.DoesNotExist:
                user = None

        elif email:
            try:
                user = User.model_objects.get(email=email)

            except User.DoesNotExist:
                user = None

        if not user or not user.check_password(password):
            return None

        return user

