# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from forms import SignupForm, RegisterForm, SearchFilterForm,\
     SubirFotoForm, ReportConcernForm
from MP100.portal.models import Redes_Sociales
from MP100.fotos.models import Foto, Categoria, Comentario,\
     UserProfile, Ganador_Votos, Voto, Temporada, Estadistica, TopAmbassador, \
     GranGanador, PanoramicWinner
from MP100.fotos.forms import SearchPhotosForm
from MP100.common.utils import direct_response, make_password, \
     sendHtmlMail
from MP100 import captcha
from zinnia.feeds import CategoryEntries
from zinnia.models import Category
import random
import re
from datetime import date, datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode
from djangobb_forum.models import Topic, Post
from servicios.models import Opinion, Servicio, Actividad, AdministradorServicio
from servicios.forms import BusquedaForm, LoginForm, RecuperarForm
#estos campos de las redes sociales se crean
#automaticamente al sincronizar la DB


redes_sociales = Redes_Sociales.objects.all()
url_redes_sociales = {}
url_redes_sociales['Facebook'] = redes_sociales.get(nombre='Facebook').url
url_redes_sociales['Twitter'] = redes_sociales.get(nombre='Twitter').url
url_redes_sociales['Flickr'] = redes_sociales.get(nombre='Flickr').url

form_register = RegisterForm();
# codigo captcha
html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)

def index(request):
    fotos_preferidas = Foto.objects.filter(estado=u'M').order_by('-id')[:16]

    slides = [list(fotos_preferidas[i*4:i*4+4]) for i in range(0, 4)]
    statistics = Estadistica.objects.get_or_create(id=1)[0]

    if Temporada().get_Current_Voting_Temporada():
        last_votes = Voto.objects.filter(alive=True).order_by("-id")[:2]
        atomfeeds = fotos_preferidas[:3]
    else:
        last_votes = []
        atomfeeds = fotos_preferidas[:5]

    dictionary = {'domain': request.META['HTTP_HOST'],
		  'form_register': form_register,
		  'atomfeeds': atomfeeds,
                  'last_votes': last_votes,
		  'allVotes': statistics.nro_total_votos,
		  'allFotos': statistics.nro_fotos_subidas,
                  'concurso_home':'_selected',
                  'topTenAmbassadors':TopAmbassador().get_last_top_10(),
		  'html_captcha': html_captcha,
		  'slides': slides,
		  'url_redes_sociales': url_redes_sociales,
                  "actividades": Actividad.objects.all()[:5]}

    if request.GET:
	if 'gclid' in request.GET:
	    return HttpResponseRedirect(reverse('main_portal'))
	
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
            #I put this 'if' trying to close a bug '/' about key error
            if 'error' in request.GET:
                dictionary['error']= request.GET['error']
	
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended'] 

    #return HttpResponse(request.GET['form_register'])

    #este update esta convirtiendo los u'' en [u''] lo que malogra la validacio
    #dictionary.update(request.GET)
    #return HttpResponse('request.GET.items: %s dictionary_items: %s ' %
    #(request.GET.items(), dictionary.items()))
    return render_to_response('portal/index/index.html', dictionary,
                                context_instance=RequestContext(request))

def redirect_index(request):
    return HttpResponseRedirect(reverse('main_portal'))  

def new_index(request):
    """
    muestra el nuevo home que direcciona a los distintos modulos del la app
    """
    atomfeeds = Foto.objects.filter(estado=u'M').order_by('-id')[:3]

    servicios = Servicio.accepted.filter(destacado=True)
    if servicios:
        slider = {"index": random.randint(0, len(servicios)-1)}
    else:
        slider = {"index": 0}
    if servicios:
        slider["img"] = servicios[slider["index"]].foto_panoramica.generate_url("pano")
        slider["url"] = servicios[slider["index"]].get_absolute_url()
        slider["des"] = "%s ..."  % servicios[slider["index"]].descripcion[:74]
    else:
        slider["img"] = u"%sdump_images/slider.jpg" % settings.MEDIA_URL

    form_login=error=''
    serLogin_form = LoginForm()
    recuperar_form = RecuperarForm()
    if request.method == "POST":
        if 'login' in request.POST:
            form_login = SignupForm(request.POST)
            if form_login.is_valid():
                try:
                    pre_user = User.objects.get(
                        email=form_login.cleaned_data['email'])
                    username = pre_user.username
                except:
                    username = ""
                password1 = form_login.cleaned_data['password']
                user = authenticate(username=username, password=password1)
                if user is not None:
                    if user.is_active:
                        # user login
                        login(request, user)
                        user_profile = user.get_profile()
                        request.session['django_language'] = user_profile.idioma
                        translation.activate(user_profile.idioma)
                    else:
                        # Return a 'disabled account' error message
                        error = _(u'This user account is disabled.')
                else:
                    # Return an 'invalid login' error message.
                    error = u'No se pudo iniciar sesión. Revise su nombre de  usuario y contraseña.'
            else:
                #error = u'El formulario no es valido'
                error = u'No se pudo iniciar sesión. Ingrese su nombre de usuario y contraseña'
        elif 'login_services' in request.POST:            
            serLogin_form = LoginForm(request.POST)
            if serLogin_form.is_valid():
                user = authenticate(username=serLogin_form.cleaned_data['email'],
                                    password=serLogin_form.cleaned_data['contrasena'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        #return HttpResponseRedirect(reverse("ser_perfil_privado"))
                    else:
                        serLogin_form.errors["email"] = [_(u"Your user account has not \
                                                            been activated, check your \
                                                            e-mail")]
                else:
                    serLogin_form.errors["email"] = [_(u"Your username or password is \
                                                       incorrect")]
        elif "recuperar" in request.POST:
            recuperar_form = RecuperarForm(request.POST)
            if recuperar_form.is_valid():
                try:
                    usuario = AdministradorServicio.objects.get(
                        user__email=recuperar_form.cleaned_data['email'])
                    sendHtmlMail("info@machu-picchu100.com",
                                 _(u"New password for Machu Picchu 100"),
                                 "ser_recuperar_mail.html",
                                  {"usuario": usuario,
                                   "password": make_password(),
                                   "sitio": Site.objects.get_current()},
                                 recuperar_form.cleaned_data['email'],
                                 path="servicios/email_templates/")
                except AdministradorServicio.DoesNotExist:
                    recuperar_form.errors["email"] = [_(u"The e-mail account does not \
                                                      belong to any registered manager")]

    if "busqueda" in request.session:
        busqueda = request.session["busqueda"]
    else:
        busqueda = {"direccion": _(u"all locations"), "tipo": None,
                    "latitud": "-16.3167", "longitud": "-71.55",
                    "filtro": "puntuacion"}
    try:
        domain = request.META['HTTP_HOST']
    except:
        domain = Site.objects.get(id=1).domain
    dictionary = {
        'domain': domain,
        'form_register': form_register,
        'form_login': form_login,
        'error': error,
        'atomfeeds': atomfeeds,
        'topTenAmbassadors':TopAmbassador().get_last_top_10(),
        'html_captcha': html_captcha,
        'url_redes_sociales': url_redes_sociales,
        "actividades": Actividad.objects.all()[:5],
        "slider": slider,
        "busqueda_form":BusquedaForm(),
        'busqueda':busqueda,
        'serLogin_form':serLogin_form,
        'recuperar_form':recuperar_form,
        'posts': Post.objects.order_by("-id")[:3],
    }

    if request.GET:
        if 'gclid' in request.GET:
            return HttpResponseRedirect(reverse('main_portal'))

        # if 'form_login' in request.GET:
        #     dictionary['form_login']=request.GET['form_login']
        #     dictionary['error']= request.GET['error']

        # if 'datos_incorrectos' in request.GET:
        #     dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
        # if 'new_pass_sended' in request.GET:
        #     dictionary['new_pass_sended']= request.GET['new_pass_sended']

    #este update esta convirtiendo los u'' en [u''] lo que malogra la validacio
    #dictionary.update(request.GET)
    #return HttpResponse('request.GET.items: %s dictionary_items: %s ' %
    #(request.GET.items(), dictionary.items()))
    return render_to_response('portal/index/newIndex.html', dictionary,
                                context_instance=RequestContext(request))


#def index_usuarios(request):
#    usuarios = User.objects.order_by('-date_joined')
#    if request.method == 'POST':
#	form = SearchFilterForm(request.POST)
#	if form.is_valid():
#	    usuarios=form.apply_filters(usuarios)
#    else:
#	form = SearchFilterForm()
#    lista_usuarios = form.paginate_list(request, usuarios,8)
#    
#    lista_usuarios.object_list = form.get_ordered_list(
#        lista_usuarios.object_list,4)
#    return render_to_response('portal/usuarios/usuarios.html',
#                              {'lista_usuarios': lista_usuarios,'form':form,},
#                              context_instance=RequestContext(request))
   
def registro(request):
    """
    Registra un nuevo usuario, luego inicia su sesion, le envía un correo con
    sus credenciasles y lo redirecciona al main_portal
    """
    statistics = Estadistica.objects.get_or_create(id=1)[0]
    result = ('','')
    captcha_error = u""
    successful_register=False;
    if request.method == 'POST':
        # Check the captcha
        check_captcha = captcha.submit(
            request.POST['recaptcha_challenge_field'],
            request.POST['recaptcha_response_field'],
            settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            # Captcha is wrong show a error ...
            captcha_error = _(u"Written words are incorrect")

        form_register = RegisterForm(request.POST, request.FILES)
	result = form_register.is_valid()
        if result[0] and not captcha_error:
            form_register.save()
	    successful_register=True
	    user = authenticate(
                username=form_register.cleaned_data['username'],
                password=form_register.cleaned_data['password1'])
	    #login(request, user)
	    #se envia el mail con los datos
	    data = {'user_firstname': user.first_name,
		    'email': user.email,
		    'password': form_register.cleaned_data['password1'],
		    'mydomain': request.META['HTTP_HOST'],
		    'encryptedUsername': urlsafe_b64encode(str(user.id)),
		    'encryptedEmail': urlsafe_b64encode(str(user.email))}
	    if user.get_profile().idioma == u'es':
		subject = u'Machu Picchu 100 - Gracias por Registrarte!'
		template = "a-photo-registering_es.html"
	    else:
		subject = u"Machu Picchu 100 - Thank you for Registering!"
		template = "a-photo-registering_en.html"
	    sendHtmlMail("info@machu-picchu100.com", subject,
                         template,
			 data, user.email)
    else:
        form_register = RegisterForm()
    #return HttpResponse(result[0])
    #form_login = u''
    atomfeeds = []
    # elección de fotos para el slide
    fotos_preferidas = Foto.objects.filter(estado=u'M').order_by(
        'num_favoritos')[:16]
    slides = [list(fotos_preferidas[i*4:i*4+4]) for i in range(0, 4)]    
    category_query_set = Category.objects.all()
    if category_query_set:
	if get_language() == 'es' and category_query_set.filter(slug='es'):
	    atomfeeds = CategoryEntries().items(
                category_query_set.filter(slug='es')[0])[:3]
	elif get_language() == 'en' and category_query_set.filter(slug='en'):
	    atomfeeds = CategoryEntries().items(
                category_query_set.filter(slug='en')[0])[:3]
    # codigo captcha
    #html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)

    args = {#'form_login': form_login,
	    'domain': request.META['HTTP_HOST'],
            'form_register': form_register,
            'atomfeeds': atomfeeds,
	    'allVotes': statistics.nro_total_votos,
	    'allFotos': statistics.nro_fotos_subidas,	    
            'html_captcha': html_captcha,
            'captcha_error': captcha_error,
            'error_size': result[1],
	    'slides': slides,
	    'url_redes_sociales': url_redes_sociales,
            'successful_register': successful_register}

    if request.GET:
	if 'form_login' in request.GET:
	    args['form_login']=request.GET['form_login']
	    args['error']= request.GET['error']
	
	if 'datos_incorrectos' in request.GET:
	    args['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    args['new_pass_sended']= request.GET['new_pass_sended'] 

    #get = urlencode(args)
    #return redirect("%s?%s" % (request.POST['redirect'], get))
    return render_to_response('portal/index/index.html', args,
                                context_instance=RequestContext(request))    

def validar_usuario(request):
    error = u""
    form_login = SignupForm()

    def errorHandle(error):
        args = {'error' : error,
                'form_login':form_login,
                #'form_search':form_search,
		#'form_register':form_register,
                #'atomfeeds': atomfeeds
		}
        get = urlencode(args)
	##caso donde el logeo en el blog da algun error
	if (re.search(u'/blog/',request.POST['redirect'])):
	    return redirect("%s?%s" % ('/', get))
	##	
        return redirect("%s?%s" % (request.POST['redirect'], get))

    if request.method == 'POST': # If the form has been submitted...
        #estos mensaje de error no es estan traduciendo xq en el template
        #templates\portal\index\base_index.html.py:301 ya se definio
        #un solo mensaje de error
        form_login = SignupForm(request.POST) # A form bound to the POST data
        if form_login.is_valid(): # All validation rules pass
            try:
                pre_user = User.objects.get(
                    email=form_login.cleaned_data['email'])
                username = pre_user.username
            except:
                username = ""
            password1 = form_login.cleaned_data['password']
            user = authenticate(username=username, password=password1)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login(request, user)
                    user_profile = UserProfile(user=user)
                    request.session['django_language'] = user_profile.idioma
                    translation.activate(user_profile.idioma)
#                    args = {'error' : error,
#                            'form_login':form_login,
#                            #'form_search':form_search,
#			    #'form_register':form_register,
#                            #'atomfeeds': atomfeeds,
#			    }
#		    get = urlencode(args)
#                    return redirect("%s?%s" % (request.POST['redirect'], get))
		    return redirect(request.POST['redirect'])
                else:
                    # Return a 'disabled account' error message
                    error = u'Esta cuenta de usuario esta deshabilidata.'
                    return errorHandle(error)
            else:
                # Return an 'invalid login' error message.
                error = u'No se pudo iniciar sesión. Revise su nombre de \
                usuario y contraseña.'
                #return HttpResponse(error)
                return errorHandle(error)
        else:
            #error = u'El formulario no es valido'
            error = u'No se pudo iniciar sesión. Ingrese su nombre de usuario \
            y contraseña'
            #return HttpResponse(error)
            return errorHandle(error)
    else:
        args = {'error' : error,
                'form_login':form_login,
                #'form_search':form_search,
		#'form_register':form_register,
                #'atomfeeds': atomfeeds
		}
        get = urlencode(args)
	##para que no genere error cuando un gracioso escribe de frente
	##la url machu-picchu100.com/validation/
	if 'redirect' not in request.POST:
	    request.POST=request.POST.copy()
	    request.POST['redirect']=u'/'
	##caso donde el logeo en el blog da algun error
	if (re.search(u'/blog/',request.POST['redirect'])):
	    return redirect("%s?%s" % ('/', get))
	##

        return redirect("%s?%s" % (request.POST['redirect'], get))

@csrf_exempt
def recuperar_password(request, password=None, username=None):
    """
    Cambia la contraseña de un usuario enviándole una nueva por correo
    """
    form_login = SignupForm()
    error = u""
    dictionary={'form_login': form_login,
		'error': error,}
    
    # Cambiar la contraseña al confirmar el e-mail
    if password and username:
        #usuario = User.objects.get(username=urlsafe_b64decode(str(username)))
	usuario = User.objects.get(id=urlsafe_b64decode(str(username)))
        usuario.set_password(password)
        usuario.save()
        return HttpResponseRedirect(reverse('main_portal'))    
    
    # Enviar un e-mail con una nueva contraseña - aún no se cambia
    if request.method == 'POST':
        try:
            usuario = User.objects.get(email=request.POST['username'])
            password = make_password(6)
            data = {'user_firstname': usuario.first_name,
		    'new_pass':password, 'mydomain': request.META['HTTP_HOST'],
		    'username': usuario.username,
		    'email': usuario.email,
		    'encryptedUsername': urlsafe_b64encode(str(usuario.id))}
	    
	    if usuario.get_profile().idioma == u'en':
		subject = u"Machu Picchu 100 - Forgotten password request "
		template = 'a-photo-recoverPassword_en.html'
	    else:
		subject = u"Machu Picchu 100 - Contraseña Olvidada"
		template = 'a-photo-recoverPassword_es.html'
	    sendHtmlMail("info@machu-picchu100.com", subject,
			 template, data, usuario.email)	    
	    dictionary['new_pass_sended']=True
        except ObjectDoesNotExist:
	    dictionary['datos_incorrectos']=True
            return HttpResponse("error")
	get = urlencode(dictionary)
        return HttpResponse("email")
	#return redirect("%s?%s" % (request.POST['redirect'], get))
    return HttpResponse("Bad Request")
#return redirect(reverse('main_portal'))

@csrf_exempt
def activate_userAccount(request, email=None, username=None):
    """
    Activa la cuenta de usuario de un usuario
    """
    if email and username:
	user = get_object_or_404(User, id=urlsafe_b64decode(str(username)))
	if user.email == urlsafe_b64decode(str(email)) and not user.is_active:
	    user.is_active = True
	    user.save()
	    return HttpResponseRedirect(reverse('new_main_portal'))    
    raise Http404    

@csrf_exempt
def stopContestComunications(request, username=None):
    """
    decodifica al username y establece en su userprofile
    el atributo accept_email_updates en False, para que ya no reciba
    comunicaciones del concurso ni de los auspiciadores
    """
    if username:
	try:
	    #usuario = User.objects.get(username=urlsafe_b64decode(str(username)))
	    usuario = User.objects.get(id=urlsafe_b64decode(str(username)))
	    profile=usuario.get_profile()
	    profile.accept_email_updates = False
            profile.accept_sponsors_emails = False
	    profile.save()
	except ObjectDoesNotExist:
	    0
	return redirect(reverse('new_main_portal'))
########################################################################################################	
	
#def ver_rrss(request):
#    form_login = SignupForm()
#    return render_to_response('portal/menu_views/rrss/rrss_view.html', {
#                    'form_login':form_login,
#                    'url_redes_sociales':url_redes_sociales,},
#                    context_instance=RequestContext(request)
#                              )

#def ver_bases(request):
#    form_login = SignupForm()
#    return render_to_response('portal/menu_views/bases/bases_view.html', {
#                    'form_login':form_login,
#                    'url_redes_sociales':url_redes_sociales,},
#                    context_instance=RequestContext(request)
#                              )
    
#def ver_noticias(request):
#    return object_list(
#        request,
#        Noticia.objects.order_by('-fecha'),
#        paginate_by=3,
#        template_name='portal/menu_views/noticias/noticia_list.html',
#        extra_context={'form_login':SignupForm(),
#                       'url_redes_sociales':url_redes_sociales,} )
#    
#def noticia_detallada(request, object_id):
#    return object_detail(
#        request,
#        Noticia.objects.all(),
#        object_id,
#        template_name='portal/menu_views/noticias/noticia_detail.html',
#        extra_context={'form_login':SignupForm(),
#                       'url_redes_sociales':url_redes_sociales,}
#        )
 
#def json_click_banner(request, banner_id):
#    """
#    Aumenta el contador de clicks de un banner
#    """
#    banner = Banner.objects.get(id=banner_id)
#    banner.add_click()
#    data = {'response': True}
#
#    return json_response(data)
    
    
#def ver_organizadores_auspiciadores(request):
#    form_login = SignupForm()
#    return render_to_response(
#        'portal/menu_views/organizadores_auspiciadores/auspiciadores.html', {
#        'form_login':form_login,
#        'url_redes_sociales':url_redes_sociales,},
#        context_instance=RequestContext(request)
#        )

#def sobre_MP(request):
#    form_login = SignupForm()
#    return render_to_response(
#        'portal/menu_views/sobre_machu_picchu/sobre_MP.html', {
#        'form_login':form_login,
#        'url_redes_sociales':url_redes_sociales,},
#        context_instance=RequestContext(request)
#        )    

#def ver_galeria(request, categoria_id=1):
#    """
#    Asegura q la categoria este en el rango de opciones, en caso contrario
#    asigna la 1ra que este en la tabla de Categoria
#    Muestra las 5 fotos al azar cada categoria, si no hay ninguna foto
#    retorna una lista_fotos vacia
#    """
#    queryset = Categoria.objects.all()
#    categoria = queryset.filter(id = categoria_id)
#    if not categoria:
#        categoria = queryset[0]
#    else:
#        categoria = categoria[0]
#    lista_fotos= categoria.foto_set.all()
#    rand_fotos=[]
#    foto_0_nro_votos = 0
#    if lista_fotos:
#        for i in range(5):
#            rand_fotos.append(random.choice(lista_fotos))
#        foto_0_nro_votos= rand_fotos[0].fans.all().count()        
#    form_login = SignupForm()
#    return render_to_response('portal/menu_views/galeria/ver_galeria.html', {
#                    'lista_categorias':queryset,
#                    'lista_fotos': rand_fotos,
#                    'foto_0_nro_votos': foto_0_nro_votos,
#                    'form_login':form_login,
#                    'url_redes_sociales':url_redes_sociales,},
#                    context_instance=RequestContext(request)
#                              )

# def ver_galeria_vote(request, categoria_id=-1):
#     """
#     Asegura q la categoria este en el rango de opciones, en caso contrario
#     asigna la 1ra que este en la tabla de Categoria
#     Muestra  fotos al azar cada categoria, 16 por pagina, si no hay ninguna
#     foto retorna una lista_fotos vacia
#     Inicialmente muestra todas las fotos sin filtrar por categoria
#     """
#     queryset = Categoria.objects.all()
#     categoria = queryset.filter(id = categoria_id)
#     if not categoria:
#         #categoria = queryset[0]
# 	lista_fotos = Foto.objects.filter(estado='M').filter(
#             temporada_habilitado='S')
#     else:
#         categoria = categoria[0]
# 	lista_fotos= categoria.foto_set.filter(estado='M').filter(
#             temporada_habilitado='S')
#     rand_fotos=[]
#     foto_0_nro_votos = 0
#     if lista_fotos:
# 	rand_fotos = lista_fotos.order_by("-id")
#     form_login = SignupForm()
#     form = SearchFilterForm()
#     lista_fotos = form.paginate_list(request, rand_fotos, 16)
#     lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list, 4)
    
#     return render_to_response('portal/menu_views/galeria/ver_votar.html', {
#                     'lista_categorias':queryset,
#                     'lista_fotos': lista_fotos,
#                     'form_login':form_login,
#                     'url_redes_sociales':url_redes_sociales,},
#                     context_instance=RequestContext(request)
#                               )

#@csrf_exempt
#def navegar_foto(request, object_id, foto_id):
#    """
#    Muestra una foto con todas sus opciones según el usuario que subió la foto y
#    el código esta
#    Verifica que los ids no hayan sido alterados y esten dentro del rango
#    actual,
#    en caso contrario redirecciona al portal_galeria_vote
#    """
#    
#    form_login = SignupForm()    
#    query = User.objects.all()
#    queryset = query.filter(id = object_id)    
#    if not queryset or not queryset[0].fotos.filter(id = foto_id):
#        return HttpResponseRedirect(reverse('main_user'))
#    user = query.get(id = object_id)
#
#    cliente = user.get_profile()
#    foto = get_object_or_404(Foto, id=foto_id)
#    fans = foto.fans.all()
#    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
#    is_comentado = False
#    #usuario = UserProfile.objects.get(user=request.user)
#    #usuario = request.user.get_profile()
#    
#    usuario_perfil = ""
#    if request.user.is_authenticated():
#        usuario_perfil = request.user.get_profile()
#    fav = foto.allFans()
#    
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
#    now = datetime.now()
#    is_temporada = False
#    lista_temporadas = Temporada.objects.all()
#    if lista_temporadas:
#        for temporada in lista_temporadas:
#            if temporada.is_in_this_temporada(now):
#                is_temporada = True
#        
#    form = ComentarioForm()
#
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
#                                                              
#
#    return render_to_response('portal/menu_views/galeria/navegar_foto.html',
#                            {'usuario': user,
#                            'foto': foto,
#                            'foto_id': foto_id,
#                            'fans': fans,
#                            'es_favorito': usuario_perfil in fav,
#                            'total_favoritos': fav.count(),
#                            'comentarios': comentarios,
#                            'is_comentado': is_comentado,
#                            'is_temporada': is_temporada,
#                            'form': form,
#			    'domain': request.META['HTTP_HOST'],
#			    'form_login':form_login,
#			    'url_redes_sociales':url_redes_sociales,},
#			    context_instance=RequestContext(request)
#			  )

#def proxima_temporada(request, categoria_id=-1):
#    """
#    Muestra las fotos que entran en la sgte temporada
#    """
#    queryset = Categoria.objects.all()
#    categoria = queryset.filter(id = categoria_id)
#    if not categoria:
#	lista_fotos = Foto.objects.filter(estado='M').filter(
#            temporada_habilitado='N')
#    else:
#        categoria = categoria[0]
#	lista_fotos= categoria.foto_set.filter(estado='M').filter(
#            temporada_habilitado='N')
#    rand_fotos=[]
#    foto_0_nro_votos = 0
#    if lista_fotos:
#	rand_fotos = lista_fotos.order_by("-id")
#    form_login = SignupForm()
#    form = SearchFilterForm()
#    lista_fotos = form.paginate_list(request, rand_fotos, 16)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list, 4)
#    
#    return render_to_response(
#        'portal/menu_views/galeria/ver_proxima_temporada.html', {
#        'lista_categorias':queryset,
#        'lista_fotos': lista_fotos,
#        'form_login':form_login,
#        'url_redes_sociales':url_redes_sociales,},
#        context_instance=RequestContext(request)
#        )
    
@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('new_main_portal'))
    
def subir_fotos(request):
    queryset = Categoria.objects.all()
    result=('','')
    
    if request.method == 'POST' and request.user.is_authenticated():
        request.POST['codigo_user'] = request.user.id
        form = SubirFotoForm(request.POST, request.FILES,
                             initial={'codigo_user':request.user.id})
#        return HttpResponse(request.FILES['foto'])
        result = form.is_valid()
        if result[0]:
            form.save()
            return HttpResponseRedirect(reverse('portal_subir_fotos_exito'))
    else:
        form = SubirFotoForm()

    dictionary={
        'domain': request.META['HTTP_HOST'],
        'error_imagen': result[1],
        'form':form,
        'form_register': form_register,
        'html_captcha': html_captcha,
        'url_redes_sociales':url_redes_sociales,
        'lista_categorias':queryset.exclude(nombre='Professional'),
        'categoria_pro': queryset.filter(nombre='Professional')[0],
        'concurso_home': '_selected',
        'very_last_temporada':  Temporada().actualTemp_is_the_last_temporada(),
        'constest_finished': Temporada().all_VotingPeriods_has_passed()}
    
    if request.GET:	
	dictionary['form_login']=request.GET['form_login']
	dictionary['error']= request.GET['error']	
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
	
    return render_to_response('portal/menu_views/enter/a-enter.html',
			      dictionary,
			      context_instance=RequestContext(request))
@login_required    
def subir_fotos_exito(request):
    return render_to_response('portal/menu_views/enter/a-enter-successful.html',
                              {'concurso_home': '_selected',
                               'domain': request.META['HTTP_HOST'],
			       'url_redes_sociales':url_redes_sociales,
			       'form_register': form_register,
			       'html_captcha': html_captcha,},
			      context_instance=RequestContext(request))
    
def vote(request):
    """
    Muestra la galeria de imagenes con el form de busqueda
    excluye las de categoria profesional
    y las que ya son ganadoras de alguna temporada
    """
    list_categories = Categoria.objects.all()
    fotos = Foto.objects.filter(estado='M').filter(
        temporada_habilitado='S').order_by("-id")
    fotos = fotos.exclude(categoria__nombre='Professional').exclude(
        ganadora_temporada__isnull=False)
    if request.method == 'GET':
        form = SearchPhotosForm(request.GET)
        if form.is_valid():
            fotos = form.apply_filters(fotos)
    else:
        form = SearchPhotosForm()
    #lista_fotos = form.paginate_list(request, fotos, 16)
    #lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,4)

    dictionary=	{'domain': request.META['HTTP_HOST'],
                 #'lista_fotos': lista_fotos,
                 'concurso_home': '_selected',
                 'lista_fotos': fotos,		
                 'lista_categorias': list_categories,
                 'form':form,
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']    
    return render_to_response('portal/menu_views/vote/a-vote.html',
			       dictionary,
			       context_instance=RequestContext(request))

@csrf_exempt    
def photo_vote(request, user_id, foto_id, mis_fotos):
    """
    Muestra una foto para ser votada si esta habilitada y moderada
    tambien si el usuario esta logeado muestra el link
    para reportar la foto
    """
    list_categories = Categoria.objects.all()
    form = SearchPhotosForm()
    form_concern = ReportConcernForm()
    flag_report_sended = False
    if request.method == "POST" and request.user.is_authenticated():
	request.POST = request.POST.copy() 
	request.POST['codigo_user'] = u'%i' % request.user.id
	request.POST['codigo_foto'] = foto_id
	temporada = Temporada().get_current_temporada()
	if temporada:
	    request.POST['codigo_temporada'] = u'%i' % temporada.id
	form_concern = ReportConcernForm(request.POST)
	if form_concern.is_valid():
	    form_concern.save()
	    flag_report_sended = True
    cliente = UserProfile.objects.get(user__id=user_id)
    foto = get_object_or_404(Foto, id=foto_id)
    fans = foto.fans()
    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
    is_comentado = False
    usuario = ""
    if request.user.is_authenticated():
	usuario = UserProfile.objects.get(user=request.user)

    #fav = foto.allFans()
    
    # El usuario viendo sus fotos
    self_user = False
    if request.user.is_authenticated():
	if cliente.user.username == usuario.user.username:
	    self_user = True
    
    # Aumentar el número de visitas a la foto una sóla vez por sesión
    key = u"foto_%s" % foto_id
    if key in request.session:
        request.session[key] = False
    else:
        request.session[key] = True
        request.session.set_expiry(0)
        foto.add_vista()

    now = datetime.now()
    is_temporada = False
    lista_temporadas = Temporada.objects.all()
    if lista_temporadas:
        for temporada in lista_temporadas:
            if temporada.is_in_this_temporada(now):
                is_temporada = True

    dictionary={'usuario': cliente,
                'domain': request.META['HTTP_HOST'],
                'lista_categorias': list_categories,
                'form':form,
                'form_concern': form_concern,
                'flag_report_sended': flag_report_sended,
                'concurso_home':'_selected',
                'foto':foto,
                'foto_id':foto_id,
                'self_user': self_user,
                'fans':fans,
                'is_temporada': is_temporada,
                'url_redes_sociales':url_redes_sociales,
                'form_register': form_register,
                'html_captcha': html_captcha,}

    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/vote/a-photo-vote.html',
			       dictionary,
			       context_instance=RequestContext(request))

#reemplazada
#def professional_photos(request):
#    """
#    Muestra la galeria de fotos profesionales con el form de busqueda
#    """
#    fotos = Foto.objects.filter(estado='M').filter(
#    categoria__nombre='Professional').order_by("?")
#    if request.method == 'POST':
#        form = SearchPhotosForm(request.POST)
#        if form.is_valid():
#            fotos = form.apply_filters(fotos)
#    else:
#        form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 16)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,4)
#
#    dictionary={'domain': request.META['HTTP_HOST'],
#	       'lista_fotos': lista_fotos,
#	       'form':form,
#	       'url_redes_sociales':url_redes_sociales,
#	       'form_register': form_register,
#	       'html_captcha': html_captcha,}
#
#    if request.GET:
#	if 'form_login' in request.GET:
#	    dictionary['form_login']=request.GET['form_login']
#	if 'error' in request.GET:
#	    dictionary['error']= request.GET['error']
#	if 'datos_incorrectos' in request.GET:
#	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
#	if 'new_pass_sended' in request.GET:
#	    dictionary['new_pass_sended']= request.GET['new_pass_sended']    
#    return render_to_response(
#               'portal/menu_views/vote/a-vote-professional.html',
#			      dictionary,
#			      context_instance=RequestContext(request))

@csrf_exempt    
def photo_vote_professional(request, user_id, foto_id):
    """
    muestra la foto panoramica individual
    """
    form = SearchPhotosForm()
    form_concern = ReportConcernForm()
    flag_report_sended = False
    if request.method == "POST" and request.user.is_authenticated():
	request.POST = request.POST.copy() 
	request.POST['codigo_user'] = u'%i' % request.user.id
	request.POST['codigo_foto'] = foto_id
	temporada = Temporada().get_current_temporada()
	if temporada:
	    request.POST['codigo_temporada'] = u'%i' % temporada.id
	form_concern = ReportConcernForm(request.POST)
	if form_concern.is_valid():
	    form_concern.save()
	    flag_report_sended = True    
    cliente = UserProfile.objects.get(user__id=user_id)
    foto = get_object_or_404(Foto, id=foto_id)
    fans = foto.fans()
    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
    is_comentado = False
    usuario = ""
    if request.user.is_authenticated():
	usuario = UserProfile.objects.get(user=request.user)
    
    #fav = foto.allFans()

    
    # El usuario viendo sus fotos
    self_user = False
    if request.user.is_authenticated():
	if cliente.user.username == usuario.user.username:
	    self_user = True
    
    # Aumentar el número de visitas a la foto una sóla vez por sesión
    key = u"foto_%s" % foto_id
    if key in request.session:
        request.session[key] = False
    else:
        request.session[key] = True
        request.session.set_expiry(0)
        foto.add_vista()

    now = datetime.now()
    is_temporada = False
    lista_temporadas = Temporada.objects.all()
    if lista_temporadas:
        for temporada in lista_temporadas:
            if temporada.is_in_this_temporada(now):
                is_temporada = True

    dictionary={'usuario': cliente,
	       'domain': request.META['HTTP_HOST'],
	       'form':form,
	       'form_concern': form_concern,
	       'flag_report_sended': flag_report_sended,
                'concurso_winners':'_selected',
	       'foto':foto,
	       'foto_id':foto_id,
	       'self_user': self_user,
	       'fans':fans,
	       'is_temporada': is_temporada,
	       'url_redes_sociales':url_redes_sociales,
	       'form_register': form_register,
	       'html_captcha': html_captcha,}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-photo-vote-professional.html',
        dictionary,
        context_instance=RequestContext(request))

#def panoramic_photos(request):
#    """
#    Muestra la galeria de fotos panoramicas con el form de busqueda
#    habilitadas y no habilitadas para la temporada,
#    pero todas moderadas
#    Ademas excluye a las fotos ganadoras 
#    """
#    list_categories = Categoria.objects.all()
#    fotos = Foto.objects.filter(estado='M').filter(panoramica=True).exclude(
#ganadora_temporada__isnull=False).order_by("?")
#    if request.method == 'POST':
#        form = SearchPhotosForm(request.POST)
#        if form.is_valid():
#            fotos = form.apply_filters(fotos)
#    else:
#        form = SearchPhotosForm()
#    lista_fotos = form.paginate_list(request, fotos, 16)
#    lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,4)
#
#    dictionary={'domain': request.META['HTTP_HOST'],
#	       'lista_categorias': list_categories,
#	       'lista_fotos': lista_fotos,
#	       'form':form,
#	       'url_redes_sociales':url_redes_sociales,
#	       'form_register': form_register,
#	       'html_captcha': html_captcha,}
#    if request.GET:
#	if 'form_login' in request.GET:
#	    dictionary['form_login']=request.GET['form_login']
#	if 'error' in request.GET:
#	    dictionary['error']= request.GET['error']
#	if 'datos_incorrectos' in request.GET:
#	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
#	if 'new_pass_sended' in request.GET:
#	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
#	    
#    return render_to_response('portal/menu_views/vote/a-vote-panoramic.html',
#			      dictionary,
#			      context_instance=RequestContext(request))
    
@csrf_exempt    
def photo_vote_panoramic(request, user_id, foto_id):
    """
    muestra la foto panoramica individual
    en el template se considera si esta habilitada o no para mostrar o no
    el boton de vote
    """
    list_categories = Categoria.objects.all()
    form = SearchPhotosForm()
    form_concern = ReportConcernForm()
    flag_report_sended = False
    if request.method == "POST" and request.user.is_authenticated():
	request.POST = request.POST.copy() 
	request.POST['codigo_user'] = u'%i' % request.user.id
	request.POST['codigo_foto'] = foto_id
	temporada = Temporada().get_current_temporada()
	if temporada:
	    request.POST['codigo_temporada'] = u'%i' % temporada.id
	form_concern = ReportConcernForm(request.POST)
	if form_concern.is_valid():
	    form_concern.save()
	    flag_report_sended = True        
    cliente = UserProfile.objects.get(user__id=user_id)
    foto = get_object_or_404(Foto, id=foto_id)
    fans = foto.fans()
    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
    is_comentado = False
    usuario = ""
    if request.user.is_authenticated():
	usuario = UserProfile.objects.get(user=request.user)
	
    #fav = foto.allFans()
    
    # El usuario viendo sus fotos
    self_user = False
    if request.user.is_authenticated():
	if cliente.user.username == usuario.user.username:
	    self_user = True
    
    # Aumentar el número de visitas a la foto una sóla vez por sesión
    key = u"foto_%s" % foto_id
    if key in request.session:
        request.session[key] = False
    else:
        request.session[key] = True
        request.session.set_expiry(0)
        foto.add_vista()

    now = datetime.now()
    is_temporada = False
    lista_temporadas = Temporada.objects.all()
    if lista_temporadas:
        for temporada in lista_temporadas:
            if temporada.is_in_this_temporada(now):
                is_temporada = True

    dictionary={'usuario': cliente,
                'domain': request.META['HTTP_HOST'],
                'lista_categorias': list_categories,
                'concurso_winners':'_selected',
                'form':form,
                'form_concern': form_concern,
                'flag_report_sended': flag_report_sended,
                'foto':foto,
                'foto_id':foto_id,
                'self_user': self_user,
                'fans':fans,
                'is_temporada': is_temporada,
                'url_redes_sociales':url_redes_sociales,
                'form_register': form_register,
                'html_captcha': html_captcha,}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']	
    return render_to_response(
        'portal/menu_views/winners/a-photo-vote-panoramic.html',
        dictionary,
        context_instance=RequestContext(request))

def next_voting_period_photos(request):
    """
    Muestra la galeria de nuevas fotos para la siguiente temporada
    Excluye a las profesionales
    """
    list_categories = Categoria.objects.all()
    fotos = Foto.objects.filter(estado='M').filter(
        temporada_habilitado='N').exclude(
        categoria__nombre='Professional').order_by('-id')
    if request.method == 'GET':
        form = SearchPhotosForm(request.GET)
        if form.is_valid():
            fotos = form.apply_filters(fotos)
    else:
        form = SearchPhotosForm()
    #lista_fotos = form.paginate_list(request, fotos, 16)
    #lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,4)

    dictionary={'domain': request.META['HTTP_HOST'],
	       'lista_categorias': list_categories,
	       #'lista_fotos': lista_fotos,
	       'lista_fotos': fotos,
	       'form':form,
	       'url_redes_sociales':url_redes_sociales,
	       'form_register': form_register,
	       'html_captcha': html_captcha,}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']    
    return render_to_response(
        'portal/menu_views/vote/a-vote-next_voting_period.html',
        dictionary,
        context_instance=RequestContext(request))

@csrf_exempt    
def photo_vote_next_voting_period(request, user_id, foto_id):
    """
    muestra la foto que estara en la sgte temporada
    """
    list_categories = Categoria.objects.all()
    form = SearchPhotosForm()
    form_concern = ReportConcernForm()
    flag_report_sended = False
    if request.method == "POST":
	request.POST = request.POST.copy() 
	request.POST['codigo_user'] = u'%i' % request.user.id
	request.POST['codigo_foto'] = foto_id
	temporada = Temporada().get_current_temporada()
	if temporada:
	    request.POST['codigo_temporada'] = u'%i' % temporada.id
	form_concern = ReportConcernForm(request.POST)
	if form_concern.is_valid():
	    form_concern.save()
	    flag_report_sended = True    
    cliente = UserProfile.objects.get(user__id=user_id)
    foto = get_object_or_404(Foto, id=foto_id)
    fans = foto.fans()
    comentarios = Comentario.objects.filter(estado=u"M", foto__id=foto_id)
    is_comentado = False
    usuario = ""
    if request.user.is_authenticated():
	usuario = UserProfile.objects.get(user=request.user)
	
    #fav = foto.allFans()
    # El usuario viendo sus fotos
    self_user = False
    if request.user.is_authenticated():
	if cliente.user.username == usuario.user.username:
	    self_user = True
    
    # Aumentar el número de visitas a la foto una sóla vez por sesión
    key = u"foto_%s" % foto_id
    if key in request.session:
        request.session[key] = False
    else:
        request.session[key] = True
        request.session.set_expiry(0)
        foto.add_vista()

    now = datetime.now()
    is_temporada = False
    lista_temporadas = Temporada.objects.all()
    if lista_temporadas:
        for temporada in lista_temporadas:
            if temporada.is_in_this_temporada(now):
                is_temporada = True
		
    dictionary={'usuario': cliente,
		'domain': request.META['HTTP_HOST'],
		'lista_categorias': list_categories,
		'form':form,
		'form_concern': form_concern,
		'flag_report_sended': flag_report_sended,
		'foto':foto,
		'foto_id':foto_id,
		'self_user': self_user,
		'fans':fans,
		'is_temporada': is_temporada,
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha,}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']    
    return render_to_response(
        'portal/menu_views/vote/a-photo-vote-next_voting_period.html',
        dictionary,
        context_instance=RequestContext(request))

def winners(request, temp_id="1"):
    """
    retorna la lista de fotos ganadoras de la temporada temp_id, junto
    con el número de temporada temp_id, así como los números de la
    temporada anterior y siguiente (la siguiente de la última es la
    primera, y la anterior de la primera es al última)
    """
    num_temporadas = Temporada.objects.all().count()
    fotos=[]
    t = Temporada().get_last_temporada()
    past_temp=''
    if t:
        past_temp=t.id
    #past_temp=Temporada().get_last_temporada().id
    if not past_temp:
        past_temp=1
    if not temp_id:
	temp_id=past_temp
    else:
	temp_id=int(temp_id)
    try:
	temporada = Temporada.objects.get(id=temp_id)
	fotos = temporada.foto_set.order_by("-num_favoritos")
    except:
	temp_id=-1
	if num_temporadas > 0:
	    temp_id=1
	    temporada = Temporada.objects.get(id=temp_id)
	    fotos = temporada.foto_set.order_by("-num_favoritos")
    prev_temp=next_temp=0
    if temp_id != -1:
	if temp_id > 1:
	    prev_temp = temp_id - 1
	else:
	    prev_temp = num_temporadas
	if temp_id < num_temporadas:
	    next_temp = temp_id + 1
	else:
	    next_temp = 1
    
    dictionary=	{'domain': request.META['HTTP_HOST'],
                 'lista_fotos': fotos,
                 'concurso_winners': '_selected',
                 'temp_id': temp_id,
                 'Next_temp': next_temp,
                 'Prev_temp': prev_temp,
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-winners_grand_final.html',
        dictionary,
        context_instance=RequestContext(request))


def finalists(request):
    """
    muestra una página con la lista de las 
    finalistas ganadores(osea con atributo winner = True) elegidas entre las
    fotos ganadoras 
    """
    fotos = GranGanador.objects.filter(winner=True)
    dictionary=	{'domain': request.META['HTTP_HOST'],
                 'lista_fotos': fotos,
                 'concurso_winners': '_selected',
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-winners_finalists.html',
        dictionary,
        context_instance=RequestContext(request))

def special_winners(request, Model, template):
    """
    Muestra los ganadores de la categoría profesional
    """
    special_mentions=[]
    if template == "a-winners_panoramic.html":
        #li=[6868,9699,10569]
        li=[25,26,27]
        #li=[1,4,5,7]
        try:
            special_mentions=[ PanoramicWinner.objects.get(id=i) for i in li ]
        except:
            special_mentions=[]
    return direct_response(request, "portal/menu_views/winners/%s" % template,
                           {'lista_fotos': Model.objects.filter(winner=True),
                            'special_mentions':special_mentions,
                            'concurso_winners':'_selected',
                            'url_redes_sociales': url_redes_sociales,
		                    'form_register': form_register,
		                    'html_captcha': html_captcha})


def mp100_special_awards(request):
    """
    muestra la vista de los premios especiales del concurso
    """
    dictionary=	{'concurso_winners':'_selected',
                 'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']

    return render_to_response('portal/menu_views/winners/a-winners_mp100_SA.html',
			       dictionary,
			       context_instance=RequestContext(request))

def grand_prize(request):
    """
    muestra la vista del premio al gran ganador
    """
    dictionary=	{'concurso_winners':'_selected',
                 'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/prizes/a-grand_prize.html',
			       dictionary,
			       context_instance=RequestContext(request)) 
    
def professional_intro(request):
    """
    muestra la vista introductoria a las fotos profesionales
    """
    dictionary=	{'concurso_winners':'_selected',
                 'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-winners_professional_intro.html',
        dictionary,
        context_instance=RequestContext(request))    

def professional_fotos(request):
    """
    muestra la vista con las fotos profesionales
    """
    fotos = Foto.objects.filter(estado='M').filter(
        categoria__nombre='Professional').order_by("-id")    
    if request.method == 'GET':
        form = SearchPhotosForm(request.GET)
        if form.is_valid():
            fotos = form.apply_filters(fotos)
    else:
        form = SearchPhotosForm()
    #lista_fotos = form.paginate_list(request, fotos, 16)
    #lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,4)
    
    dictionary=	{'domain': request.META['HTTP_HOST'],
		 'lista_fotos': fotos,
                 'concurso_winners':'_selected',
		 'form': form,
		 'url_redes_sociales':url_redes_sociales,
		 'form_register': form_register,
		 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-winners_professional_fotos.html',
        dictionary,
        context_instance=RequestContext(request))    

def panoramic_intro(request):
    """
    muestra la vista introductoria a las fotos panoramicas
    """
    dictionary=	{'concurso_winners':'_selected',
                 'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-winners_panoramic_intro.html',
        dictionary,
        context_instance=RequestContext(request))



def panoramic_fotos(request):
    """
    muestra la vista con las fotos panoramicas
    """
    list_categories = Categoria.objects.all()
    fotos = Foto.objects.filter(estado='M').filter(
        panoramica=True).exclude(ganadora_temporada__isnull=False).order_by("-id")
    if request.method == 'GET':
        form = SearchPhotosForm(request.GET)
        if form.is_valid():
            fotos = form.apply_filters(fotos)
    else:
        form = SearchPhotosForm()
    #lista_fotos = form.paginate_list(request, fotos, 16)
    #lista_fotos.object_list = form.get_ordered_list(lista_fotos.object_list,4)

    dictionary={'concurso_winners':'_selected',
                'domain': request.META['HTTP_HOST'],
                'lista_categorias': list_categories,
                'lista_fotos': fotos,
                'form': form,
                'url_redes_sociales':url_redes_sociales,
                'form_register': form_register,
                'html_captcha': html_captcha,}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
	    
    return render_to_response(
        'portal/menu_views/winners/a-winners_panoramic_fotos.html',
        dictionary,
        context_instance=RequestContext(request))


def panoramic_prize(request):
    """
    muestra la vista del permio de las fotos panorámicas
    """
    dictionary=	{'concurso_winners':'_selected',
                 'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']

    return render_to_response('portal/menu_views/prizes/a-prizes_panoramic.html',
			       dictionary,
			       context_instance=RequestContext(request))    

def kunas_gifts(request):
    """
    muestra la página con el detalle de los regalos de Kuna
    """
    ul_id=[2478,2368,1538,268,2020,3009,128,385,6459,151,173,185,360,370,503,
           6937,629,747,1930,2031,4209,4210,6459,336,556,8592,5497,7819,619]
    #ul_id = []
    users_list = [ User.objects.get(id=i) for i in ul_id ]
    dictionary=	{'concurso_winners':'_selected',
        'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha,
                 'lista_users': users_list,
                 'FLAG_PATH':settings.FLAG_PATH,}
    # if request.GET:
    #     if 'form_login' in request.GET:
    #         dictionary['form_login']=request.GET['form_login']
    #     if 'error' in request.GET:
    #         dictionary['error']= request.GET['error']
    #     if 'datos_incorrectos' in request.GET:
    #         dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
    #     if 'new_pass_sended' in request.GET:
    #         dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
        'portal/menu_views/winners/a-kunas-gifts.html',
        dictionary,
        context_instance=RequestContext(request))    


def votingWinners(request, temp_id="1"):
    """
    retorna la lista de ganadores por sorteo de la temporada temp_id, junto
    con el número de temporada temp_id, así como los números de la
    temporada anterior y siguiente (la siguiente de la última es la
    primera, y la anterior de la primera es al última)
    """
    num_temporadas = Temporada.objects.all().count()
    user_list=[]
    t=Temporada().get_last_temporada()
    past_temp=''
    if t:
        past_temp=t.id
#    past_temp=Temporada().get_last_temporada().id
    if not past_temp:
        past_temp=1
    if not temp_id:
        temp_id=past_temp
    else:
	temp_id=int(temp_id)
    try:
	temporada=Temporada.objects.get(id=temp_id)
	user_list = temporada.get_winners_from()
    except:
	temp_id=-1
	if num_temporadas > 0:
	    temp_id=1
	    temporada=Temporada.objects.get(id=temp_id)
	    user_list = temporada.get_winners_from()
    prev_temp=next_temp=0
    if temp_id != -1:
	if temp_id > 1:
	    prev_temp = temp_id - 1
	else:
	    prev_temp = num_temporadas
	if temp_id < num_temporadas:
	    next_temp = temp_id + 1
	else:
	    next_temp = 1
    
    dictionary=	{'domain': request.META['HTTP_HOST'],
                 'lista_users': user_list,
                 'concurso_winners':'_selected',
                 'temp_id': temp_id,
                 'Next_temp': next_temp,
                 'Prev_temp': prev_temp,
                 'FLAG_PATH':settings.FLAG_PATH,
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/winners/a-winners_votingWinners.html',
			       dictionary,
			       context_instance=RequestContext(request))

def votingWinnersPrize(request):
    """
    muestra la vista del premio a los ganadores por votar
    """
    dictionary=	{'concurso_winners':'_selected',
                 'domain': request.META['HTTP_HOST'],
                 'url_redes_sociales':url_redes_sociales,
                 'form_register': form_register,
                 'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/prizes/a-prizes_votingWinners.html',
			       dictionary,
			       context_instance=RequestContext(request))

def sponsors(request, item_id):
    """
    muestra la vista de los patrocinadores
    """
    if not item_id or (item_id not in [u'1',u'2',u'3',u'4',u'5','6']):
	item_id=1
    template_name = {
	2: 'a-Org&Spon_sponsors2.html',
	3: 'a-Org&Spon_sponsors3.html',
	4: 'a-Org&Spon_sponsors4.html',
        5: 'a-Org&Spon_sponsors5.html',
        6: 'a-Org&Spon_sponsors6.html',
    }.get(int(item_id), 'a-Org&Spon_sponsors1.html')

    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/organizadores_auspiciadores/%s'
			      % template_name,
			       dictionary,
			       context_instance=RequestContext(request))

def organizers(request):
    """
    muestra la vista de los organizadores
    """
    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/organizadores_auspiciadores/a-Org&Spon_organizers.html',
			       dictionary,
			       context_instance=RequestContext(request))

def social_responsability(request, item_id):
    """
    muestra la vista de los organizadores
    """
    if not item_id or (item_id != u'1' and item_id !=u'2'):
	item_id=1
    if item_id == 1:
	template_name = 'a-Org&Spon_social_responsability.html'
    else:
	template_name = 'a-Org&Spon_social_responsability_cartuc.html'
    
    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/organizadores_auspiciadores/%s'
			      % template_name,
			       dictionary,
			       context_instance=RequestContext(request))

def contest_details(request):
    """
    muestra la vista de los organizadores
    """
    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response('portal/menu_views/organizadores_auspiciadores/a-Org&Spon_contestDetails.html',
			       dictionary,
			       context_instance=RequestContext(request))

def final_prizes(request):
    """
    muestra la vista de los organizadores
    """
    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
	'portal/menu_views/prizes/a-prizes_final.html',
	 dictionary,context_instance=RequestContext(request))

#@append_custom_context
def all_final_prizes(request, extra_context={}):
   """
   Page 44 Contest prizes
   """
   return render_to_response(
       'portal/menu_views/prizes/a-prizes_final.html', extra_context,
       context_instance=RequestContext(request))

def site_activity_stream(request):
    """
    Muestra la página con todas las últimas actividades de realizadas
    en el site
    """
    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,}
    listListAmbassadors = [UserProfile.objects.order_by("-points")[i*3:i*3+3] for i in range(0,3)]
    photosList = Foto.objects.filter(estado='M').filter(
        temporada_habilitado='S').order_by("-id")[:5]
    votoList = Voto.objects.filter(alive=True).order_by("-id")[:5]
    topicsList = Topic.objects.all()[:5]
    opinionsList = Opinion.objects.filter(moderado=True).order_by("-id")[:2]
    servicesList = Servicio.objects.order_by("-id")[:3]
    dictionary['listListAmbassadors']=listListAmbassadors    
    dictionary['photosList'] = photosList
    dictionary['votoList'] = votoList
    dictionary['topicsList'] = topicsList
    dictionary['opinionsList'] = opinionsList
    dictionary['servicesList'] = servicesList
    dictionary['concurso_act_str']= '_selected'
    return render_to_response(
        'portal/menu_views/site_activity_stream/a-site_activity_stream.html', 
        dictionary, context_instance=RequestContext(request))


#@append_custom_context
def history(request, item_id, extra_context={}):
    """
    Page 44 About Machu Picchu - History
    """
    if not item_id or (item_id not in [u'1',u'2',u'3',u'4']):
	item_id=1
    template_name = {
	2: 'Peru.html',
	3: 'Trivia.html',
	4: 'Videos.html',
    }.get(int(item_id), 'MachuPicchu.html')  
    extra_context['concurso_mpp'] = '_selected'
    return render_to_response(
        'portal/menu_views/about/%s' % template_name, extra_context,
        context_instance=RequestContext(request))
    
def faqs(request):
    """
    muestra la vista de preguntas frecuentes
    """
    dictionary=	{'domain': request.META['HTTP_HOST'],
		'url_redes_sociales':url_redes_sociales,
		'form_register': form_register,
		'html_captcha': html_captcha}
    if request.GET:
	if 'form_login' in request.GET:
	    dictionary['form_login']=request.GET['form_login']
	if 'error' in request.GET:
	    dictionary['error']= request.GET['error']
	if 'datos_incorrectos' in request.GET:
	    dictionary['datos_incorrectos']= request.GET['datos_incorrectos']
	if 'new_pass_sended' in request.GET:
	    dictionary['new_pass_sended']= request.GET['new_pass_sended']
    return render_to_response(
	'portal/menu_views/faqs/a-faqs.html',
	 dictionary,context_instance=RequestContext(request))

    
def calcular(request):
    """
    funcionamiento del conjob de fin de temporada
    """
    finished_temporada=Temporada().get_last_temporada()
    if finished_temporada:
    #10 ganadores mas votados (o mas si hay empate en 10mo lugar)
	fotos = Foto.objects.filter(
            temporada_habilitado='S').exclude(
            ganadora_temporada__isnull=False).order_by("-num_favoritos")
	if fotos:
	    winners=fotos[:10]
	    #verificando empates
	    #si hay empate en 10 lugar, todos los que tengan por lo menos
            # ese puntaje pasan
	    nro=-1
	    for winner in winners:
		nro+=1
	    if fotos.filter(
                num_favoritos=winners[nro].num_favoritos).count() > 1:
		winners=fotos.filter(
                    num_favoritos__gte=winners[nro].num_favoritos)
	    for winner in winners:
		finished_temporada.foto_set.add(winner)
		
    #ganador o ganadores por sorteo (antes era por votos)
	contestants = finished_temporada.get_contestants()
	vote_winners=[]
	if contestants:
	    if contestants.count() <=10:
		vote_winners = contestants[:10]
	    else:
		flag = 1
		accepted=False
		while flag <= 5:
		    rand_choice = random.choice(contestants)
		    while rand_choice in vote_winners:
			rand_choice = random.choice(contestants)
		    vote_winners.append(rand_choide)
		    rand_choice = random.choice(contestants)
		    while rand_choice in vote_winners:
			rand_choice = random.choice(contestants)
		    vote_winners.append(rand_choide)
		    contestants = contestants.exclude(
                        userprofile__me_gusta_temp__leq=flag)
		    if contestans:
			0
		    else:
			contestants = finished_temporada.get_contestants()
		    if flag==5:
			if len(vote_winners) < 10:
			    rest = 10-len(vote_winners)
			    contestants = finished_temporada.get_contestants()
			    while rest > 0:
				rand_choice = random.choice(contestants)
				while rand_choice in vote_winners:
				    rand_choice = random.choice(contestants)
				vote_winners.append(rand_choide)
				rest-=1
		    flag+=1
		    
	    for vote_winner in vote_winners:
		m = Ganador_Votos.objects.create(temporada=finished_temporada,
						 user=vote_winner)			
	#old method
	#contestants = finished_temporada.get_contestants()
	#vote_winners=[]
	#if contestants:
	#    max_votes=0
	#    for contestant in contestants:
	#	tmp = contestant.get_profile()\
        #.get_total_votes_of_my_votes_in_this_temporada(finished_temporada.id)
	#	if tmp == max_votes:
	#	    vote_winners.append(contestant)		    
	#	if tmp > max_votes:
	#	    vote_winners=[]
	#	    vote_winners.append(contestant)
	#	    max_votes = tmp
	#    if max_votes != 0:
	#	for vote_winner in vote_winners:
	#	    m = Ganador_Votos.objects.create(
        #temporada=finished_temporada,
	#			      user=vote_winner,
	#			      num_votos=max_votes)
    #num_favoritos=0, excepto para ganadores
	fotos_to_reset = Foto.objects.filter(
            temporada_habilitado='S').exclude(ganadora_temporada__isnull=False)
	for foto in fotos_to_reset:
	    foto.reset_num_favoritos()

    #LOS TEMPLATES ENVITAN QUE SE SUBAN FOTOS SI NO HAY UNA PROXIMA TEMPORADA
    #Escenarios respecto a uploaded photos:
    #1.- se crea un nuevo usuario
    #		1.1.- no hay temporadas actuales ni proximas
    #			no debe subir fotos, uploaded_photos = 0
    #		1.2.- hay una temporada actual y no proxima
    #			no debe subir fotos, uploaded_photos = 0
    #		1.3.- hay una temporada proxima y no actual
    #			debe subir foto, uploaded_photos = 0
    #		1.4.- hay una temporada actual y uotra proxima
    #			debe subir foto, uploaded_photos = 0
    #		RESUMEN: siempre uploaded_photos = 0
    #2.- se inicia una temporada
    #		todos los uploades_photos = 0, para q puendan subir a la sgte,
    #haiga o no
    #3.- finaliza una temporada
    #		3.1.- haiga o no temporadas sgtes no se hace nada xq al
    #iniciarse ya
    #			se pusieron todo los uploades_photos = 0, para q
    #puendan subir a la sgte, haiga o no
    #			NADA
    #4.- se crea una nueva temporada (siguiente) y:
    #		4.1.- hay temporada actual pero no sgte
    #			NADA, abarcado por 2
    #		4.2.- hay temporada actual y ya una sgte
    #			NADA
    #		4.3.- no hay actual
    #			NADA, abaracado por 1 y 2
    #			(si nunca hubo una temporada, entonces toods estan
    #listos para subir)
    #			(si hubo una temporada, al iniciarse todos estan
    #listos para volver a subir)
    #		RESUMEN: NADA
    #5.- hay usuarios registrados
    #		5.1.- no hay temporadas
    #			NADA, templates controlan ya esta abarcado por 1
    
    #habilitar todas las fotos que noe stan habilitadas
	fotos_not_enabled = Foto.objects.filter(temporada_habilitado="N")
	for foto in fotos_not_enabled:
	    foto.enable()
	    
    #reinicia el contador de votos de los usuarios
	contestants = finished_temporada.get_contestants()
	if contestants:
	    for contestant in contestants:
		contestant.get_profile().clear_season()

    return render_to_response('portal/ppp.html', {},
                              context_instance=RequestContext(request))
    
def inicio_temp(request):
    """
    funcionamiento del cron job de inicio de temporada
    """
    list_userprofile = UserProfile.objects.filter(uploaded_photos__gt=0)
    for userprofile in list_userprofile:
	userprofile.reset_uploaded_photos()    
    
    return render_to_response('portal/ppp.html', {},
                              context_instance=RequestContext(request))

#@append_custom_context
def bases(request, extra_context={}):
    template_name = 'portal/bases.html'
    if request.LANGUAGE_CODE == 'es':
        template_name = 'portal/bases_es.html'
    return render_to_response(template_name, extra_context,
                              context_instance=RequestContext(request))

#@append_custom_context
def most_voted(request, extra_context={}):
    """
    muestra la pagina con las 100 fotos mas votadas
    """
    extra_context['lista_fotos']=Foto.objects.filter(estado='M').filter(
        temporada_habilitado='S').exclude(
	ganadora_temporada__isnull=False).exclude(
	categoria__nombre='Professional').order_by("-num_favoritos")[:100]
    return render_to_response('portal/menu_views/most_voted/a-mv-most_voted.html',
			      extra_context, context_instance=RequestContext(request))

#@append_custom_context
def top_ten(request, extra_context={}):
    """
    muestra la pagina con las 10 fotos mas votadas
    """
    extra_context['lista_fotos']=Foto.objects.filter(estado='M').filter(
        temporada_habilitado='S').exclude(
	ganadora_temporada__isnull=False).exclude(
	categoria__nombre='Professional').order_by("-num_favoritos")[:10]
    return render_to_response('portal/menu_views/most_voted/a-mv-top_ten.html',
			      extra_context, context_instance=RequestContext(request))
    
#@append_custom_context
def uploads_today(request, extra_context={}):
    """
    muestra la pagina con las fotos subidas hoy
    """
    hoy = date.today()
    hoy = datetime(hoy.year, hoy.month, hoy.day)
    extra_context['lista_fotos']=Foto.objects.filter(estado='M').filter(
        temporada_habilitado='S').exclude(
	ganadora_temporada__isnull=False).exclude(
	categoria__nombre='Professional').filter(fecha__gte=hoy)
    return render_to_response('portal/menu_views/most_voted/a-mv-uploads_today.html',
			      extra_context, context_instance=RequestContext(request))

