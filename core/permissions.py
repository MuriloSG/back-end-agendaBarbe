from rest_framework import permissions
from users.models import User

class IsBarber(permissions.BasePermission):
    """
    Permite acesso apenas a usuários do tipo BARBER.
    """
    def has_permission(self, request, view):
        return request.user.profile_type == User.Perfil.BARBER


class IsClient(permissions.BasePermission):
    """
    Permite acesso apenas a usuários do tipo CLIENTE.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.profile_type == User.Perfil.CLIENT
