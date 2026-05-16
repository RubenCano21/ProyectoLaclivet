"""
Backend de autenticación personalizado para usar email en lugar de username
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class EmailBackend(ModelBackend):
    """
    Permite autenticación usando email en lugar de username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autenticar usuario usando email o username
        Prioriza email, pero también acepta username como fallback
        """
        # Si se proporciona explícitamente un email
        email = kwargs.get('email')

        # Intentar obtener el usuario por email
        if email:
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return None
        # Si se proporciona username, intentar como email primero
        elif username:
            # Verificar si parece un email (contiene @)
            if '@' in username:
                try:
                    user = Usuario.objects.get(email=username)
                except Usuario.DoesNotExist:
                    return None
            else:
                # Si no es email, buscar por username
                try:
                    user = Usuario.objects.get(username=username)
                except Usuario.DoesNotExist:
                    return None
        else:
            return None

        # Verificar la contraseña
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

