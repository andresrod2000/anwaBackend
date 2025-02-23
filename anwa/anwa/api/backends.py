from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CaseInsensitiveEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Permite autenticación por correo insensible a mayúsculas/minúsculas."""
        if username:
            username = username.lower()  # Convierte el correo a minúsculas
        try:
            user = UserModel.objects.get(correo=username)  # Asegúrate de usar 'correo', no 'email'
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        """Django usa esto para obtener el usuario autenticado."""
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
