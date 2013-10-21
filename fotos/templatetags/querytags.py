#-*- coding: utf-8 -*-

from django import template
from MP100.fotos.models import ComentarioPerfil

register = template.Library()

@register.inclusion_tag('common/templatetags/comentarios_perfil.html')
def get_comentarios_perfil(cliente_id):
    """
    Retorna los comentarios hechos en un perfil
    """
    comentarios = ComentarioPerfil.objects.filter(cliente__user__id=cliente_id).order_by("-fecha")
    
    return {'comentarios': comentarios}
