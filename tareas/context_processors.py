from .models import PerfilUsuario

def perfil_usuario(request):
    if request.user.is_authenticated:
        try:
            return {'user_profile': request.user.perfil}
        except PerfilUsuario.DoesNotExist:
            return {'user_profile': None}
    return {'user_profile': None}