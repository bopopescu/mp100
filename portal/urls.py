# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from MP100.portal.views import *
from MP100.portal.decorators import get_ajax_login_form, get_ajax_register_form
from fotos.models import PanoramicWinner, ProfessionalWinner

urlpatterns = patterns('',
    url(r'^photo_contest/$', index, name='main_portal'),
    url(r'^$', new_index, name='new_main_portal'),
    url(r'^ajax/login_form/', get_ajax_login_form, name="ajax_login_form"),
    url(r'^ajax/register_form/', get_ajax_register_form,
        name="ajax_register_form"),
    #url(r'^terminos/$', index_terminos, name="index_terminos"),
    #url(r'^faq/$', index_faq, name="index_faq"),
    url(r'^register/$', registro, name='registro'),
    #url(r'^register/$',
    #    CompleteRegisterForm([TerminosCondicionesForm, RegisterForm]),
    #    name='registro'),
    #url(r'^register/$',
    #    CompleteRegisterForm([TerminosCondicionesForm, RegisterForm]),
    #                        {'extra_context' : {'form_login':SignupForm(),
    #                                            'url_redes_sociales':url_redes_sociales,}},
    #    name='registro'),
    url(r'^subir_fotos/$', subir_fotos, name="portal_subir_fotos"),
    url(r'^subir_fotos_exito/$', subir_fotos_exito,
        name="portal_subir_fotos_exito"),
    url(r'^vote/$', vote, name="portal_vote"),
    url(r'^photo_vote/(?P<user_id>\d+)/(?P<foto_id>\d+)/(?P<mis_fotos>\d+)/$',
        photo_vote, name="portal_photo_vote"),
    #reemplazada
    #url(r'^professional_photos/$', professional_photos,
    #    name="portal_professional_photos"),
    url(r'^professional_photo/(?P<user_id>\d+)/(?P<foto_id>\d+)/$',
        photo_vote_professional, name="portal_photo_vote_professional"),    
    url(r'^panoramic_photo_vote/(?P<user_id>\d+)/(?P<foto_id>\d+)/$',
        photo_vote_panoramic, name="portal_photo_vote_panoramic"),
    url(r'^next_voting_period/$', next_voting_period_photos,
        name="portal_next_voting_period"),
    url(r'^next_voting_period_photo_vote/(?P<user_id>\d+)/(?P<foto_id>\d+)/$',
        photo_vote_next_voting_period,
        name="portal_photo_vote_next_voting_period"),
    url(r'^winners/$', finalists, name="portal_finalists"), 
    url(r'^finalists/(?P<temp_id>\d+)?$', winners, name="portal_winners"),
    url(r'^professional_winners/$', special_winners,
        {"Model": ProfessionalWinner,
         "template": "a-winners_professional.html"},
        name="professional_winners"),
    url(r'^panoramic_winners/$', special_winners,
        {"Model": PanoramicWinner,
         "template": "a-winners_panoramic.html"},
        name="panoramic_winners"),
    url(r'^special_awards/$', mp100_special_awards,
        name='portal_mp100_special_awards'),
    url(r'^grand_prize/$', grand_prize, name="portal_grand_prize"),     
    url(r'^professional_intro/$', professional_intro,
        name="portal_professional_intro"),
    url(r'^professional_photos/$', professional_fotos,
        name="portal_professional_fotos"),
    url(r'^panoramic_intro/$', panoramic_intro,
        name="portal_panoramic_intro"),
    url(r'^kuna/$', kunas_gifts, name="portal_kunas_gifts"),
    url(r'^sony/$', panoramic_fotos, name="portal_panoramic_fotos"),
    url(r'^Sony/$', panoramic_fotos, name="portal_panoramic_fotos"),
    url(r'^SONY/$', panoramic_fotos, name="portal_panoramic_fotos"),
    url(r'^panoramic_prize/$', panoramic_prize, name="portal_panoramic_prize"),
    url(r'^voting_winners/(?P<temp_id>\d+)?$', votingWinners,
        name="portal_votingWinners"),
    url(r'^voting_winners_prize/$', votingWinnersPrize,
        name="portal_votingWinnersPrizePrize"),     
    url(r'^sponsors/(?P<item_id>\d+)?$', sponsors, name="portal_sponsors"),
    url(r'^organizers/$', organizers, name="portal_organizers"),
    url(r'^social_responsability/(?P<item_id>\d+)?$', social_responsability,
        name="portal_social_responsability"),
    url(r'^contest_details/$', contest_details,
        name="portal_contest_details"),
    url(r'^final_prizes/$', final_prizes, name='portal_final_prizes'),
    url(r'^all_final_prizes/$', all_final_prizes,
        name='all_portal_final_prizes'),
    url(r'^site_activity_stream/$', site_activity_stream, 
        name='portal_site_activity_stream'),
    # pagina 29
    url(r'^about/(?P<item_id>\d+)?$', history, name='portal_about_history'),
    url(r'^faqs/$', faqs, name='portal_faqs'),
    url(r'^bases/$', bases, name='portal_bases'),
    #BORRAR ESTAS DOS ANTES DE ENTRAR EN PRODUCCION#################
    #url(r'^calcular/$', calcular, name="portal_calcular"),
    #url(r'^inicio_temp/$', inicio_temp, name="portal_inicio_temp"),
    url(r'^most_voted/$', most_voted, name="portal_most_voted"),
    url(r'^top_ten/$', top_ten, name="portal_top_ten"),
    url(r'^uploads_today/$', uploads_today, name="portal_uploads_today"),
    ################################################################

    #url(r'^usuarios/$', index_usuarios, name='index_usuarios'),
    url(r'^register/registered/$', direct_to_template,
        {'template':'portal/register/registered.html'}, name='registrado'),
    url(r'^recuperar_password/$', recuperar_password, 
        name='recuperar_password'),
    url(r'^recuperar_password/(?P<password>[\w]+)/(?P<username>[-\_\=\w]+)/$',
        recuperar_password, name='recuperar_password'),
    url(r'^validation/$', validar_usuario, name='validar_usuario'),
    url(r'^auc/(?P<email>[-\_\=\w]+)/(?P<username>[-\_\=\w]+)/$',
        activate_userAccount, name='portal_activate_userAccount'),
    #url(r'^rrss/$', ver_rrss, name='portal_rrss'),
    #url(r'^bases/$', ver_bases, name='portal_ver_bases'),
    #url(r'^feeds/$', UltimasNoticiasFeed(), name='rss_feeds'),
    #url(r'^noticias/$', ver_noticias, name='portal_ver_noticias'),
    #url(r'^noticias/(?P<object_id>\d+)/$', noticia_detallada, 
    #    name='portal_noticia_detail'),    
    #url(r'^json_click_banner/(?P<banner_id>\d+)/$', json_click_banner, 
    #    name='json_click_banner'),
    #url(r'^galeria/(?P<categoria_id>\d+)?$', ver_galeria,
    #    name='portal_galeria_imagenes'),
    #url(r'^galeria_votar/(?P<categoria_id>\d+)?$', ver_galeria_vote,
    #    name='portal_galeria_vote'),
    #url(r'^galeria_votar/(?P<object_id>\d+)/(?P<foto_id>\d+)/$', navegar_foto,
    #    name = 'portal_navegar_foto'),
    #url(r'^proxima_temporada/(?P<categoria_id>\d+)?$', proxima_temporada ,
    #    name='portal_proxima_temporada'),
    #url(r'^organizadores/$', ver_organizadores_auspiciadores,
    #    name='portal_organizadores_auspiciadores'),
    #url(r'^sobre_MP/$', sobre_MP, name='portal_sobre_MP'),
    url(r'^msje_voto/$', direct_to_template,
        {'template': 'portal/menu_views/galeria/premios.html'},
        name= 'portal_msje_voto'),
    url(r'^logout/$', logout_view, name='logout_view'),
    url(r'^stop_comunications/(?P<username>[-\_\=\w]+)/$',
        stopContestComunications, name="portal_stopContestComunications"),
    (r'^i18n/', include('django.conf.urls.i18n')),

)

#urlpatterns += patterns('django.contrib.auth.views',		
    #url(r'^$', 'login', {'template_name': 'portal/index/index.html',},
    #    name='main_portal'),
    #url(r'^$', 'login', {'template_name': 'portal/index/index.html',
    #                     'SSL': settings.ENABLE_SSL }, name='main_portal'),
    #url(r'^accounts/login/$', 'login', {'template_name': 'registration/login.html',
    #                                    'SSL': settings.ENABLE_SSL }, name='login'),
    #url(r'^logout/$', logout_then_login, {'SSL': settings.ENABLE_SSL }, name='logout'),
#)
