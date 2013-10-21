from django.conf.urls.defaults import *
from MP100.usuario.views import *

urlpatterns = patterns('',
    url(r'^$', index, name="usuario_main_user"),
    url(r'^editar_perfil/$', editar_perfil, name='usuario_editar_perfil'),
    url(r'^editar_perfil_exito/$', editar_perfil_exito, name='usuario_editar_perfil_exito'),
    url(r'^amigos/$', amigos, name='usuario_amigos'),
    url(r'^amigos_lista/$', ver_amigos, name='usuario_ver_amigos'),
    url(r'^amigos_eliminar/$', eliminar_amigo, name='usuario_eliminar_amigo'),
    url(r'^amigos_solicitudes$', ver_solicitudes, name='usuario_ver_solicitudes'),
    url(r'^aceptar_solicitud/$', aceptar_solicitud, name='usuario_aceptar_solicitud'),
    url(r'^eliminar_solicitud/$', eliminar_solicitud, name='usuario_eliminar_solicitud'),
    url(r'^(?P<user_id>\d+)$', public_profile, name='usuario_public_profile'),
    url(r'^solicitar/$', solicitud, name='usuario_solicitud'),
    url(r'^solicitud_enviada/$', solicitud_enviada, name='usuario_solicitud_enviada'),
    url(r'^solicitud_innecesaria/$', solicitud_innecesaria, name='usuario_solicitud_innecesaria'),
    url(r'^mis_fotos/$', mis_fotos, name='usuario_mis_fotos'),
)