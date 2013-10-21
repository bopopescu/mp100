# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required 
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('MP100.admin.views',
    url(r'^select_photos_kuna/$', 'show_fotos_for_kuna',
        name="admin_show_fotos_for_kuna"),
    url('^verify_votes/$', 'verify_votes', name="admin_verify_votes"),
    url('^verify_votes/(?P<foto_id>\d+)/(?P<pais_id>\d+)?$',
        'show_all_votes', name="admin_show_all_votes"),
    url('^disqualify/$', 'disqualify_user', name="admin_disqualify_user"),
    url('^user_disqualified/$', login_required(direct_to_template), 
        {'template':'admin/verify_votes/disqualified_user.html'}, 
        name="admin_user_disqualified"),
#    url('^verify_votes_patterns/(?P<foto_id>\d+)/(?P<pattern>\w+)?$',
#       'show_all_votes_patterns', name="admin_show_all_votes_patterns"),
    #url(r'^estadisticas/$', 'estadisticas', name="admin_estadisticas"),
    #url(r'^favoritas/$', 'favoritas', name="admin_favoritas"),
    #url(r'^ganadoras_temporada/$', 'ganadora_temporada', 
    #    name="ganadora_temporada"),
    #url(r'^ganadoras_temporada/(?P<temporada_id>\d+)/$', 'ganadora_temporada', 
    #    name="ganadora_temporada_elegida"),
    #url(r'^base_datos/$', 'manage_db', name = 'admin_db'),
    #url(r'^generar_backup/$', 'generar_backup', name="admin_generar_backup" ),
    #url(r'^generar_backup_exito/$', 'generar_backup_exito',
    #    name="admin_generar_backup_exito" ),
    #url(r'^habilitar_fotos/$', 'habilitar_fotos', name="admin_habilitar_fotos" ),
    #url(r'^habilitar_fotos_exito/$', direct_to_template,
    #    {'template':'admin/habilitar_fotos/habilitar_exito.html'},
    #    name="admin_habilitar_fotos_exito" ),
    #url(r'^enviar_email/$', 'send_email', name="admin_enviar_email" ),
    #url(r'^enviar_email_exito/$', direct_to_template,
    #    {'template':'admin/send_email/success_email_send.html'},
    #    name="admin_enviar_email_exito" ),
)
