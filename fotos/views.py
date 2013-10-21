#-*- coding: utf-8 -*-
#from django.contrib.auth.models import User
#from django.shortcuts import render_to_response, get_object_or_404
#from django.template import RequestContext
from django.contrib.auth.decorators import login_required
#from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
#from django.utils.translation import ugettext as __
#from django.views.generic.list_detail import object_detail
#from django.views.decorators.csrf import csrf_exempt
#from MP100.portal.models import Redes_Sociales
#from MP100.common.utils import direct_response, json_response, send_html_mail
#from MP100.fotos.forms import ComentarioForm, EnviarMensajeForm
#from MP100.fotos.forms import UserProfileForm, SearchPhotosForm, \
#     InvitationForm, SearchDeleteFriends, CompartirFotoForm, SubirFotoForm, \
#     SearchInviteFilterForm, AddFriendForm, DeleteFriendForm, \
#     DeleteSolicitude, AcceptSolicitude, DeleteCommentForm, DeletePhotoForm
#from models import UserProfile, Foto, Noticia, Comentario, ComentarioPerfil, \
#     Temporada, Voto
#from datetime import timedelta, date, datetime
from models import Foto, Temporada, Voto, Estadistica
from MP100.common.utils import json_response

#estos campos de las redes sociales se crean
#automaticamente al sincronizar la DB
#redes_sociales = Redes_Sociales.objects.all()
#url_redes_sociales = {}
#url_redes_sociales['Facebook'] = redes_sociales.get(nombre='Facebook').url
#url_redes_sociales['Twitter'] = redes_sociales.get(nombre='Twitter').url
#url_redes_sociales['Flickr'] = redes_sociales.get(nombre='Flickr').url

#@login_required
#def index(request):
#    avatar = request.user.get_profile().foto
#    inicio_temporada = fin_temporada = datetime.now()
#    temporadas = Temporada.objects.all()
#    if temporadas:
#        tmp=temporadas[0].get_current_temporada()
#        if tmp:
#            inicio_temporada = tmp.fecha_inicio
#            fin_temporada = tmp.fecha_fin
#    return render_to_response('fotos/perfil_inicio/perfil.html',
#                              {'avatar':avatar,
#                               'url_redes_sociales': url_redes_sociales,
#                               'inicio_temporada': inicio_temporada,
#                               'fin_temporada': fin_temporada,},
#                              context_instance=RequestContext(request))

#@login_required
#def logout_view(request):
#    logout(request)
#    return HttpResponseRedirect(reverse('main_portal'))
#
#@login_required
#def editar_perfil(request):
#    result = ('','')
#    avatar = request.user.get_profile().foto
#    draw_department = False
#    if request.user.get_profile().pais.printable_name == u'Peru':
#	draw_department = True
#    return HttpResponse(draw_department)
#    if request.method == 'POST':
#        #asegurando q no se cambio el hidden user_id del form
#        if str(request.user.id) != str(request.POST['user_id']):
#                result = (False, 'No intente cambiar los campos hidden.')
#                form = UserProfileForm()
#        else:
#                form = UserProfileForm(request.POST, request.FILES)
#                #return HttpResponse(form.is_valid(request.user))
#                #result = form.is_valid(request.user)
#        result = form.is_valid()
#        if result[0]:
#            form.save(request.user)
#            return HttpResponseRedirect(reverse('main_user'))
#        else:
#            form = UserProfileForm(instance = request.user.get_profile(),
#            initial={'first_name': request.user.first_name,
#                     'last_name': request.user.last_name,
#                     'username': request.user.username,
#                     'email': request.user.email,
#                     'user_id': request.user.id,})
#            #   return HttpResponse(result[1])
#    return render_to_response('fotos/forms/editar_perfil/UserProfile_form.html',
#                              {'avatar':avatar ,
#                               'form':form,
#			       'draw_department': draw_department,
#                               'error_size': result[1],
#                               'url_redes_sociales': url_redes_sociales},
#                              context_instance=RequestContext(request))

#@login_required
#def ver_perfil(request):
#    avatar = request.user.get_profile().foto
#    return object_detail(
#            request, UserProfile.objects.all(),
#            request.user.get_profile().id,
#            template_name = 'fotos/forms/ver_perfil/UserProfile_detail.html',
#            extra_context = {'first_name': request.user.first_name ,
#                             'last_name': request.user.last_name,
#                             'username': request.user.username,
#                             'email': request.user.email,
#                             'url_redes_sociales': url_redes_sociales,
#                             'avatar':avatar,},
#                                                )

#@login_required
#def buscar(request):
#    avatar = request.user.get_profile().foto
#    usuarios = User.objects.all().order_by('-date_joined')
#    if request.method == 'POST':
#        form = SearchInviteFilterForm(request.POST)
#    if form.is_valid():
#        usuarios=form.apply_filters(usuarios)
#    else:
#        form = SearchInviteFilterForm()
#    lista_usuarios = form.paginate_list(request, usuarios, 15)
#    lista_usuarios.object_list = form.get_ordered_list(
#            lista_usuarios.object_list,5)
#    return render_to_response('fotos/forms/buscar/UserProfile_search.html',
#                              {'lista_usuarios': lista_usuarios,'form':form,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def buscar_fotos(request):
#    avatar = request.user.get_profile().foto
#    #fotos = Foto.objects.filter(estado='M').order_by('-id')
#    fotos = Foto.objects.filter(estado='M').filter(
#	    temporada_habilitado='S').order_by("?")
#    if request.method == 'POST':
#        form = SearchPhotosForm(request.POST)
#        if form.is_valid():
#            fotos = form.apply_filters(fotos)
#        else:
#            form = SearchPhotosForm()
#        lista_fotos = form.paginate_list(request, fotos, 15)
#        lista_fotos.object_list = form.get_ordered_list(
#            lista_fotos.object_list,5)
#        return render_to_response('fotos/forms/buscar_fotos/Fotos_search.html',
#                                  {'lista_fotos': lista_fotos,
#                                   'form':form,
#                                   'url_redes_sociales': url_redes_sociales,
#                                   'avatar': avatar,},
#                                  context_instance=RequestContext(request))

#@login_required
#def buscar_fotos_prox_temp(request):
#    avatar = request.user.get_profile().foto
#    fotos = Foto.objects.filter(estado='M').filter(
#        temporada_habilitado='N').order_by("?")
#    if request.method == 'POST':
#        form = SearchPhotosForm(request.POST)
#        if form.is_valid():
#            fotos = form.apply_filters(fotos)
#        else:
#            form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 15)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,5)
#    return render_to_response(
#        'fotos/forms/buscar_fotos/Fotos_search_prox_temp.html',
#        {'lista_fotos': lista_fotos,
#         'form':form,
#         'url_redes_sociales': url_redes_sociales,
#         'avatar': avatar,},
#        context_instance=RequestContext(request))

#@login_required
#def solicitud(request):
#    """
#    Envia una solicitud de amistad
#    """
#    if request.method == 'POST':
#        form = AddFriendForm(request.POST)
#        if form.is_valid(request.user):
#            if form.requires_solicitude(request.user):
#                form.save(request.user)
#                return HttpResponseRedirect(reverse('fotos_solicitud_enviada'))
#            else:
#                return HttpResponseRedirect(
#                    reverse('fotos_solicitud_innecesaria'))
#    return HttpResponseRedirect(reverse('main_user'))


#@login_required
#def solicitud_enviada(request):
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/forms/buscar/solicitud_enviada.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))
#
#@login_required    
#def solicitud_innecesaria(request):
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/forms/buscar/solicitud_innecesaria.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required    
#def subir_fotos(request):
#    avatar = request.user.get_profile().foto
#    result=('','')
#    if request.method == 'POST':
#        request.POST['codigo_user'] = request.user.id
#        form = SubirFotoForm(request.POST, request.FILES,
#                             initial={'codigo_user':request.user.id})
#        result = form.is_valid()
#        if result[0]:
#            form.save()
#            return HttpResponseRedirect(reverse('fotos_subir_fotos_exito'))
#    else:
#        form = SubirFotoForm()
#    return render_to_response('fotos/forms/subir_foto/SubirFoto_form.html',
#                              {'error_imagen': result[1],
#                               'form':form,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))
#
#@login_required
#def subir_fotos_exito(request):
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/forms/subir_foto/SubirFoto_exito.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

###############################VISTAS DEL PERFIL PUBLICO########################
#def perfil_publico(request, object_id):
#    """
#    Despliega el perfil público de la persona con id = object_id.
#    Verifica que el id este dentro del rango actual de usuarios.
#    """
#    query = User.objects.all()
#    if not query.filter(id = object_id):
#        return HttpResponseRedirect(reverse('main_user'))
#    user = query.get(id = object_id)
#    avatar = user.get_profile().foto
#    return render_to_response('fotos/perfil_publico/perfil_detail.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,
#                               'usuario': user,},
#                              context_instance=RequestContext(request))
#
#
#def ver_amigos_public(request, object_id):
#    """
#    Muestra los amigos del usuario con id = object_id
#    Sólo si está logeado da la opción de invitar
#    Verifica que el id este dentro del rango actual de usuarios.
#    """
#    query = User.objects.all()
#    if not query.filter(id = int(object_id)):
#        return HttpResponseRedirect(reverse('main_user'))
#    user = query.get(id = object_id)
#    avatar = user.get_profile().foto
#    amigos = user.get_profile().amigos.order_by('-id')
#    form = SearchDeleteFriends()
#    lista_amigos = form.paginate_list(request, amigos, 15)
#    lista_amigos.object_list = form.get_ordered_list(lista_amigos.object_list,5)
#    return render_to_response('fotos/amigos_perfil_publico/amigos_list.html',
#                              {'lista_amigos':lista_amigos,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,
#                               'usuario':user,},
#                              context_instance=RequestContext(request))
#
#def ver_fotos_public(request, object_id):
#    """
#    Muestra las fotos subidas por el usuario con id = object_id
#    Verifica que el id este dentro del rango actual de usuarios.
#    """
#    query = User.objects.all()
#    if not query.filter(id = int(object_id)):
#        return HttpResponseRedirect(reverse('main_user'))
#    user = query.get(id = object_id)
#    avatar = user.get_profile().foto
#    fotos = user.fotos.filter(estado='M').filter(
#        temporada_habilitado='S').order_by('-id')
#    form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 15)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,5)
#    return render_to_response('fotos/ver_fotos_perfil_publico/fotos_list.html',
#                              {'lista_fotos':lista_fotos,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,
#                               'usuario':user,},
#                              context_instance=RequestContext(request))

################################################################################
#
#@login_required    
#def ver_solicitudes(request):
#    avatar = request.user.get_profile().foto
#    solicitudes = request.user.solicitudes.order_by('-id')
#    form = SearchPhotosForm()
#    lista_solicitudes = form.paginate_list(request, solicitudes, 5)
#    lista_solicitudes.object_list = form.get_ordered_list(
#        lista_solicitudes.object_list,1)
#    return render_to_response('fotos/ver_solicitudes/solicitudes_list.html',
#                              {'lista_solicitudes':lista_solicitudes,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def aceptar_solicitud(request):
#    if request.method == 'POST':
#        form = AcceptSolicitude(request.POST)
#        if form.is_valid():
#            form.save(request.user)
#    return HttpResponseRedirect(reverse('fotos_ver_solicitudes'))
#
#@login_required
#def eliminar_solicitud(request):
#    if request.method == 'POST':
#        form = DeleteSolicitude(request.POST)
#        if form.is_valid():
#            form.delete(request.user)
#    return HttpResponseRedirect(reverse('fotos_ver_solicitudes'))
#
#@login_required
#def ver_amigos(request):
#    avatar = request.user.get_profile().foto
#    amigos = request.user.get_profile().amigos.order_by('-id')
#    if request.method == 'POST':
#        form = SearchDeleteFriends(request.POST)
#        if form.is_valid():
#            amigos = form.apply_filters(amigos)
#    else:
#        form = SearchDeleteFriends()
#    lista_amigos = form.paginate_list(request, amigos, 15)
#    lista_amigos.object_list = form.get_ordered_list(lista_amigos.object_list,5)
#    return render_to_response('fotos/amigos/amigos_list.html',
#                              {'form': form,
#                               'lista_amigos':lista_amigos,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def eliminar_amigo(request):
#    if request.method == 'POST':
#        form = DeleteFriendForm(request.POST)
#        if form.is_valid(request.user):
#            form.delete(request.user)
#            return HttpResponseRedirect(reverse('fotos_amigo_eliminado'))
#    return HttpResponseRedirect(reverse('fotos_amigos'))
#
#@login_required        
#def amigo_eliminado(request):
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/amigos/amigo_eliminado.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))
#
#@login_required
#def invitacion_enviada(request):
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/forms/invitacion/envio_exitoso.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def enviar_invitacion(request):
#    avatar = request.user.get_profile().foto
#    if request.method == 'POST':
#        form = InvitationForm(request.POST)
#        if form.is_valid():
#            form.send(request.user)
#            return HttpResponseRedirect(reverse('fotos_invitacion_enviada'))
#    else:
#        form = InvitationForm()
#    return render_to_response(
#        'fotos/forms/invitacion/EnviarInvitacion_form.html',
#        {'form':form,
#         'url_redes_sociales': url_redes_sociales,
#         'avatar': avatar,},
#        context_instance=RequestContext(request))
#
#@login_required
#def ver_fotos(request):
#    avatar = request.user.get_profile().foto
#    fotos = request.user.fotos.order_by('-id')
#    if request.method == 'POST':
#        form = SearchPhotosForm(request.POST)
#        if form.is_valid():
#            fotos = form.apply_filters(fotos)
#    else:
#        form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 15)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,5)
#    return render_to_response('fotos/ver_fotos/fotos_list.html',
#                              {'form': form,
#                               'lista_fotos':lista_fotos,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def ver_votos(request):
#    avatar = request.user.get_profile().foto
#    fotos = request.user.foto_set.order_by('-id')
#    if request.method == 'POST':
#        form = SearchPhotosForm(request.POST)
#        if form.is_valid():
#            fotos = form.apply_filters(fotos)
#    else:
#        form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 15)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,5)
#    return render_to_response('fotos/ver_votos/fotos_list.html',
#                              {'lista_fotos':lista_fotos,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def borrar_foto(request):
#    if request.method == 'POST':
#        form = DeletePhotoForm(request.POST)
#        if form.is_valid(request.user):
#            form.delete(request.user)
#    return HttpResponseRedirect(reverse('fotos_ver_fotos'))

#@login_required
#def borrar_comentario(request):
#    """
#    Verifica que el id del comentario no haya sido alterado, si es asi
#    lo borra y redirecciona a la misma pagina
#    sino redirecciona al main_user
#    """
#    if request.method == 'POST':
#        form = DeleteCommentForm(request.POST)
#        if form.is_valid():
#            foto_id = Comentario.objects.get(
#                id=request.POST['comentario_id']).user.id
#            form.delete()
#            return HttpResponseRedirect(
#                reverse('fotos_navegar_foto',
#                        args=[request.user.username, foto_id]))
#    return HttpResponseRedirect(reverse('main_user'))

#@login_required
#def noticias(request, tema):
#    """
#    Si la varible tema tiene otra cosa se redireccia al inicio.
#    Muestra todas las noticias creadas por el admin
#    Muestra todos los comentarios de los amigos del usuario realizados
#    con menos de un dia de antiguedad.
#    Muestra todas las fotos de los amigos del usuario subidas
#    con menos de 24hrs de antiguedad.
#    """
#    if tema not in ['notificaciones', 'comentarios', 'fotos']:
#        return HttpResponseRedirect(reverse('main_user'))
#
#    noticias = []
#    if tema == 'notificaciones':
#                noticias = Noticia.objects.order_by('-fecha')
#    if tema == 'comentarios':
#        #for user in request.user.fotos.all():
#        #    noticias.extend(user.comentario_set.filter(fecha__gte =
#        #    date.today() - timedelta(1)).filter(estado = 'M'))
#        for userprofile in request.user.get_profile().amigos.all():
#            noticias.extend(userprofile.user.comentario_set.filter(
#                fecha__gte = date.today() - timedelta(1)).filter(estado = 'M'))
#    if tema == 'fotos':
#        for userprofile in request.user.get_profile().amigos.all():
#            noticias.extend(userprofile.user.fotos.filter(
#                fecha__gte = date.today() - timedelta(1)))
#    avatar = request.user.get_profile().foto
#    form = SearchPhotosForm()
#    lista_noticias = form.paginate_list(request, noticias, 5)
#    return render_to_response('fotos/noticias/noticias_list.html',
#                              {'lista_noticias':lista_noticias,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,
#                               'tema':tema},
#                              context_instance=RequestContext(request))

#@login_required
#def ver_noticia(request, object_id):
#    """
#    Muestra una noticia con id = object_id, ademas verifica que el
#    object_id este dentro del rango válido de noticias
#    """
#    query = Noticia.objects.all()
#    if not query.filter(id = object_id):
#        return HttpResponseRedirect(reverse('fotos_noticias'))
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/noticias/noticia_detail.html',
#                              {'noticia':query.get(id = object_id),
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def enviar_mensaje(request, object_id):
#    """
#    revisa que el object_id este dentro del rango de usuarios
#    envia el mensaje al correo asociado al usuario con
#    id = object_id
#    """
#    query = User.objects.all()
#    if not query.filter(id = object_id):
#        return HttpResponseRedirect(reverse('main_user'))
#    avatar = query.get(id = object_id).get_profile().foto
#    if request.method == 'POST':
#        form = EnviarMensajeForm(request.POST)
#        if form.is_valid():
#            form.send(request.user)
#            return HttpResponseRedirect(
#                reverse('fotos_mensaje_enviado', args=[object_id]))
#        else:
#            form = EnviarMensajeForm(
#                initial={'destinatario': User.objects.get(id = object_id).email
#                         })
#    return render_to_response('fotos/mensaje/enviar_mensaje_form.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,
#                               'usuario': User.objects.get(id=object_id),
#                               'form': form,},
#                              context_instance=RequestContext(request))
#@login_required
#def mensaje_enviado(request, object_id):
#    """
#    muestra un mensaje indicando que se envio el correo exitosamente
#    """
#    query = User.objects.all()
#    if not query.filter(id = object_id):
#        return HttpResponseRedirect(reverse('main_user'))
#    avatar = query.get(id = object_id).get_profile().foto
#    return render_to_response('fotos/mensaje/mensaje_enviado.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,
#                               'usuario': query.get(id=object_id)},
#                              context_instance=RequestContext(request))

#@login_required
#def opciones_ayuda(request):
#    """
#    muestra links a todos los mini videos de ayuda
#    """
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/ayuda/ayuda_list.html',
#                              {'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def ayuda_detail(request, opcion):
#    """
#    Asegura que la opción no haya sido alterada, en caso contrario hace una
#    redirección a la vista principal
#    Muestra el mini video de cada opción
#    """
#    dict_opciones = {
#        'buscar_usuarios': 'http://www.youtube.com/watch?v=II1CkBCwy0w',
#        'buscar_fotos': 'http://www.youtube.com/watch?v=cNHu5uUbIHs',
#        'subir_fotos': 'http://www.youtube.com/watch?v=xBHeE8PRXqA',
#        'editar_perfil': 'http://www.youtube.com/watch?v=JjXXZsm7yik',
#        'mis_fotos': 'http://www.youtube.com/watch?v=Ms41APcRA7o',
#        'mis_amigos': 'http://www.youtube.com/watch?v=fLbihMF-B4Q',
#        'invitar': 'http://www.youtube.com/watch?v=da4_e6fDXXo',}
#    if opcion not in dict_opciones.keys():
#        return HttpResponseRedirect(reverse('main_user'))
#    avatar = request.user.get_profile().foto
#    return render_to_response('fotos/ayuda/ayuda_detail.html',
#                              {'object_video': {opcion: dict_opciones[opcion]},
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@login_required
#def ver_ganadores(request):
#    """muestra todos los ganadores"""
#    avatar = request.user.get_profile().foto
#    temporada = Temporada.objects.all()
#    fotos = ''
#    if temporada:
#        fotos = temporada[0].get_all_foto_winners()
#    form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 15)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,5)
#    return render_to_response('fotos/ver_ganadores/fotos_list.html',
#                              {'lista_fotos':lista_fotos,
#                               'url_redes_sociales': url_redes_sociales,
#                               'avatar': avatar,},
#                              context_instance=RequestContext(request))

#@csrf_exempt
#def navegar_foto(request, user, foto_id, mis_fotos):
#    """
#    Muestra una foto con todas sus opciones según el usuario que subió la foto y
#    el código de esta
#    """
#    avatar = request.user.get_profile().foto
#    cliente = UserProfile.objects.get(user__username=user)
#    foto = get_object_or_404(Foto, id=foto_id)
#    fans = foto.fans.all()
#    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
#    is_comentado = False
#    usuario = UserProfile.objects.get(user=request.user)
#    Voto.objects.filter(codigo_foto=foto).values_list(
#        'codigo_user__userprofile', flat=True)
#    # El usuario viendo sus fotos
#    if cliente.user.username == usuario.user.username:
#        self_user = True
#    else:
#        self_user = False
#    # Aumentar el número de visitas a la foto una sóla vez por sesión
#    key = u"foto_%s" % foto_id
#    if key in request.session:
#        request.session[key] = False
#    else:
#        request.session[key] = True
#        request.session.set_expiry(0)
#        foto.add_vista()
#    now = datetime.now()
#    is_temporada = False
#    lista_temporadas = Temporada.objects.all()
#    if lista_temporadas:
#        for temporada in lista_temporadas:
#            if temporada.is_in_this_temporada(now):
#                is_temporada = True
#
#
#    form = ComentarioForm()
#    compartir_form = CompartirFotoForm()
#    form_search = SearchPhotosForm()
#
#    if request.method == 'POST':
#        if 'texto' in request.POST:
#            form = ComentarioForm(request.POST)
#            if form.is_valid():
#                comentario = form.save(commit=False)
#                comentario.foto = foto
#                comentario.user = request.user
#                comentario.save()
#                is_comentado = True
#                form = ComentarioForm()
#
#        if 'asunto' in request.POST:
#            compartir_form = CompartirFotoForm(request.POST)
#            if compartir_form.is_valid():
#                subject = __(u"Quieren compartir una foto contigo")
#                data = (cliente,
#                        compartir_form.cleaned_data['asunto'],
#                        request.META['HTTP_HOST'],
#                        request.user.username,
#                        foto_id)
#                send_html_mail(subject, "compartir_foto.html", data,
#                               "info@machu-picchu100.com",
#                               [compartir_form.cleaned_data['email']])
#
#        return direct_response(
#            request, 'fotos/navegar_foto/navegar_foto.html',
#            {'usuario': cliente,
#             'domain': request.META['HTTP_HOST'],
#             'foto': foto,
#             'foto_id': foto_id,
#             'self_user': self_user,
#             'fans': fans,
#             'es_favorito': usuario in fav,
#             'total_favoritos': len(fav),
#             'comentarios': comentarios,
#             'is_comentado': is_comentado,
#             'is_temporada': is_temporada,
#             'form': form,
#             'mis_fotos': mis_fotos,
#             'form_search': form_search,
#             'compartir_form': compartir_form,
#             'page_title': u'Foto: %s de %s' % \
#                  (foto.titulo, cliente.user.username),
#             'avatar': avatar,})

@login_required
def json_me_gusta(request, foto_id):
    """
    Guarda un nuevo usuario en la lista de fans de una foto
    """
    usuario = request.user.get_profile()
    foto = Foto.objects.get(id=foto_id)
    if int(usuario.me_gusta_temp) >= 5:
        data = {'maximo': True}
	return json_response(data)
    else:
	temp_actual = Temporada().get_current_temporada()
	if temp_actual:
	    #foto = Foto.objects.get(id=foto_id)
	    if foto not in usuario.get_photos_voted_from_this_temporada(temp_actual):
		#foto.fans.add(request.user)
		new_voto = Voto(codigo_user=request.user,
				codigo_foto=foto,
				codigo_temporada=temp_actual)
		new_voto.save()
		usuario.nuevo_voto()
		foto.add_num_favoritos()
		Estadistica.objects.get_or_create(id=1)[0].add_voto()
		data = {'fans': foto.num_favoritos,
			'maximo': False}
                new_voto.increasePoints()
		return json_response(data)
    return HttpResponseRedirect(reverse('main_portal'))


#def json_add_favoritos(request, foto_id):
#    """
#    Guarda un foto en la lista de favoritos de un usuario
#    """
#    foto = Foto.objects.get(id=foto_id)
#    cliente = UserProfile.objects.get(user__username=request.user.username)
#    if cliente.favoritos.all().count() < 5:
#        cliente.favoritos.add(foto)
#        foto.add_num_favoritos()
#        data = {'response': True}
#    else:
#        data = {'response': False}    
#    return json_response(data)


#def json_comentar_perfil(request, usuario_id, texto):
#    """
#    Guarda un comentario en el perfil de un usuario hecho por un cliente
#    """
#    cliente = UserProfile.objects.get(user__id=usuario_id)
#    amigo = UserProfile.objects.get(user=request.user)
#    comentario = ComentarioPerfil(cliente=cliente, amigo=amigo, texto=texto)
#    comentario.save()
#    data = {'avatar': u"%s" % amigo.foto}
#    return json_response(data)


#@csrf_exempt
#def navegar_foto_publico(request, object_id, foto_id):
#    """
#    Muestra una foto con todas sus opciones según el usuario que subió la foto y
#    el código esta
#    Verifica que los ids no hayan sido alterados y esten dentro del rango
#    actual,
#    en caso contrario redirecciona al main_user o hasta el portal si el usuario
#    no esta logeado
#    """
#    query = User.objects.all()
#    queryset = query.filter(id = object_id)
#    if not queryset or not queryset[0].fotos.filter(id = foto_id):
#        return HttpResponseRedirect(reverse('main_user'))
#    user = query.get(id = object_id)
#    cliente = user.get_profile()
#    avatar = cliente.foto
#    foto = get_object_or_404(Foto, id=foto_id)
#    fans = foto.fans.all()
#    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
#    is_comentado = False
#    #usuario = UserProfile.objects.get(user=request.user)
#    #usuario = request.user.get_profile()
#    usuario_perfil = ""
#    if request.user.is_authenticated():
#        usuario_perfil = request.user.get_profile()
#    fav = Voto.objects.filter(foto=foto).values_list(
#        'codigo_user__userprofile', flat=True)
#
#    # Aumentar el número de visitas a la foto una sóla vez por sesión
#    key = u"foto_%s" % foto_id
#    if key in request.session:
#        request.session[key] = False
#    else:
#        request.session[key] = True
#        request.session.set_expiry(0)
#        foto.add_vista()
#
#    form = ComentarioForm()
#    compartir_form = CompartirFotoForm()
#    if request.method == 'POST':
#        if 'texto' in request.POST:
#            form = ComentarioForm(request.POST)
#            if form.is_valid():
#                comentario = form.save(commit=False)
#                comentario.foto = foto
#                comentario.user = request.user
#                comentario.save()
#                form = ComentarioForm()
#                is_comentado = True
#        if 'asunto' in request.POST:
#            compartir_form = CompartirFotoForm(request.POST)
#            if compartir_form.is_valid():
#                subject = __(u"Quieren compartir una foto contigo")
#                data = (cliente,
#                        compartir_form.cleaned_data['asunto'],
#                        request.META['HTTP_HOST'],
#                        request.user.username,
#                        foto_id)
#                send_html_mail(subject, "compartir_foto.html", data,
#                               "info@machu-picchu100.com",
#                               [compartir_form.cleaned_data['email']])
    #            
    #return direct_response(
    #    request,
    #    'fotos/navegar_foto_publico/navegar_foto.html',
    #    {'usuario': user,
    #     'foto': foto,
    #     'foto_id': foto_id,
    #     'fans': fans,
    #     'es_favorito': usuario_perfil in fav,
    #     'total_favoritos': len(fav),
    #     'comentarios': comentarios,
    #     'is_comentado': is_comentado,
    #     'form': form,
    #     'compartir_form': compartir_form,
    #     'page_title': u'Foto: %s de %s' % (foto.titulo, cliente.user.username),
    #     'avatar': avatar,})
