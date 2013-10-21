# Create your views here.
from django.views.generic.list_detail import object_detail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404

from datetime import timedelta, date, datetime

from MP100.fotos.forms import *
from MP100.portal.models import Redes_Sociales
from MP100.portal.forms import RegisterForm
from MP100.common.utils import direct_response, json_response, send_html_mail
from MP100.fotos.models import UserProfile, Foto, Noticia, Comentario, ComentarioPerfil, Temporada
from MP100 import captcha
from servicios.models import Servicio
import random
#estos campos de las redes sociales se crean
#automaticamente al sincronizar la DB
redes_sociales = Redes_Sociales.objects.all()
url_redes_sociales = {}
url_redes_sociales['Facebook'] = redes_sociales.get(nombre='Facebook').url
url_redes_sociales['Twitter'] = redes_sociales.get(nombre='Twitter').url
url_redes_sociales['Flickr'] = redes_sociales.get(nombre='Flickr').url

#indicador q se esta en la cta de usuario
user_account = True;
#TODO: al final eliminar todas las importaciones q no se usen

@login_required
def index(request):
    avatar = request.user.get_profile().foto
    #users that voted for your photos
    fotos=request.user.fotos.filter(alive=True)
    queryset1=[]
    if fotos:
        foto=random.choice(fotos)
        queryset1=foto.voto_set.filter(alive=True).order_by("-id")[:3]
    #photos uploaded by your friends
    friends=request.user.get_profile().amigos.all()
    queryset2=[]    
    if friends:
        friend=random.choice(friends)
        queryset2=friend.user.fotos.order_by("-fecha")[:3]
    #users that answered one of your topics
    topics=request.user.topic_set.order_by("-updated")
    queryset3=[]
    if topics:
        queryset3=[t.last_post for t in topics][:3]
    #new registered services
    queryset4=Servicio.objects.order_by("-id")[:3]
    #levels reached by your friends
    queryset5=[]
    if friends:
        queryset5=friends.order_by("?")[:3]
    listActStr = []
    listActStr.extend(queryset1)
    listActStr.extend(queryset2)
    listActStr.extend(queryset3)
    listActStr.extend(queryset4)
    listActStr.extend(queryset5)
    random.shuffle(listActStr)
    return render_to_response('fotos/perfil_inicio/a-profile.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'allTemporadas': Temporada.objects.filter(fecha_inicio__lte=datetime.now()),
                               'listActStr': listActStr[:5],
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))

@login_required
def editar_perfil(request):
    result = ('','')
    avatar = request.user.get_profile().foto
    draw_department = False
    if request.user.get_profile().pais and request.user.get_profile().pais.printable_name == u'Peru':
        draw_department = True    
    if request.method == 'POST':
        request.POST['user_id'] = u'%i' % request.user.id
        form = UserProfileForm(request.POST, request.FILES)
        result = form.is_valid()
        if result[0]:
            form.save(request.user)
            return HttpResponseRedirect(reverse('usuario_editar_perfil_exito'))
        request.POST['user_id'] = u''
    else:
        form = UserProfileForm(instance = request.user.get_profile(),
                               initial={'first_name': request.user.first_name,
                                        'last_name': request.user.last_name,
                                        'username': request.user.username,
                                        'email': request.user.email,
                                        'user_id': request.user.id,})
    return render_to_response('fotos/forms/editar_perfil/a-profile-edit.html',
                              {'avatar':avatar ,'user_account': user_account,
                               'domain': request.META['HTTP_HOST'],
                               'form':form, 'error_size': result[1],
                               'draw_department': draw_department,
                               'url_redes_sociales': url_redes_sociales},
                              context_instance=RequestContext(request))
    
@login_required
def editar_perfil_exito(request):
    avatar = request.user.get_profile().foto
    return render_to_response('fotos/forms/editar_perfil/a-profile-edit-exito.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))
    
@login_required
def amigos(request):
    avatar = request.user.get_profile().foto
    return render_to_response('fotos/amigos/a-profile-myfriends.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))

@login_required
def ver_amigos(request):
    """
    muestra todos los amigos del usuario, con la posibilidad de eliminarlos
    """
    avatar = request.user.get_profile().foto
    amigos = request.user.get_profile().amigos.order_by('-id')
    return render_to_response('fotos/amigos/a-profile-myfriends-friends.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'amigos': amigos,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))

@login_required
def eliminar_amigo(request):
    if request.method == 'POST':
        form = DeleteFriendForm(request.POST)
        if form.is_valid(request.user):
            form.delete(request.user)
    return HttpResponseRedirect(reverse('usuario_ver_amigos'))

@login_required
def ver_solicitudes(request):
    avatar = request.user.get_profile().foto
    solicitudes = request.user.solicitudes.order_by('-id')
    return render_to_response('fotos/amigos/a-profile-myfriends-friend-requests.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'solicitudes': solicitudes,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))
@login_required
def aceptar_solicitud(request):
    if request.method == 'POST':
        form = AcceptSolicitude(request.POST)
        if form.is_valid():
            form.save(request.user)
    return HttpResponseRedirect(reverse('usuario_ver_solicitudes'))    

@login_required
def eliminar_solicitud(request):
    if request.method == 'POST':
        form = DeleteSolicitude(request.POST)
        if form.is_valid():
            form.delete(request.user)
    return HttpResponseRedirect(reverse('usuario_ver_solicitudes'))

def public_profile(request, user_id):
    """
    muestra el perfil publico de un usuario
    """
    form_register = RegisterForm();
    html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)    
    usuario = get_object_or_404(User, id=user_id)
    if not usuario.is_active:
	raise Http404
	#return HttpResponseRedirect(reverse('main_portal'))
    avatar = usuario.get_profile().foto
    
    dictionary={'avatar':avatar,
                'domain': request.META['HTTP_HOST'],
                'form_register': form_register,
                'html_captcha': html_captcha,
                'usuario': usuario,
                'url_redes_sociales': url_redes_sociales,}    
    
    return render_to_response('fotos/perfil_publico/a-public-profile.html',
                              dictionary,
                              context_instance=RequestContext(request))

@login_required    
def solicitud(request):
    """
        Envia una solicitud de amistad
    """ 
    if request.method == 'POST':
        form = AddFriendForm(request.POST)
        if form.is_valid(request.user):
            if form.requires_solicitude(request.user):
                form.save(request.user)
                return HttpResponseRedirect(reverse('usuario_solicitud_enviada'))
            else:
                return HttpResponseRedirect(reverse('usuario_solicitud_innecesaria'))
    return HttpResponseRedirect(reverse('usuario_main_user'))
    
@login_required
def solicitud_enviada(request):
    avatar = request.user.get_profile().foto
    return render_to_response('fotos/perfil_inicio/a-solicitud-enviada.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))  
    
@login_required
def solicitud_innecesaria(request):
    avatar = request.user.get_profile().foto
    return render_to_response('fotos/perfil_inicio/a-solicitud-innecesaria.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))
    
@login_required
def mis_fotos(request):
    """
    muestra todas las fotos del usuario, con la posibilidad de editar su
    titulo, descripcion y ediciones
    """
    avatar = request.user.get_profile().foto
    fotos = request.user.fotos.order_by('-id')
    form = SearchPhotosForm()
    lista_fotos = form.paginate_list(request, fotos, 4)
    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,1)    
    return render_to_response('fotos/ver_fotos/a-profile-myphotos.html',
                              {'avatar':avatar,
                               'domain': request.META['HTTP_HOST'],
                               'user_account': user_account,
                               'lista_fotos': lista_fotos,
                               'url_redes_sociales': url_redes_sociales,},
                              context_instance=RequestContext(request))
