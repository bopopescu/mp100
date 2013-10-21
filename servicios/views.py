# -*- coding: utf-8 -*-

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from MP100 import captcha
from common.utils import direct_response, sendHtmlMail, json_fastsearch, \
    make_password, json_response, get_paginated
from servicios.decorators import change_password
from servicios.forms import LoginForm, BusquedaForm, ServicioPublicoForm, \
    ServicioPrivadoForm, UbicacionForm, ServicioEdicionForm, FotoForm, \
    EditFotoForm, OpinionForm, ContactoForm, RecuperarForm, \
    ServicioPanoramicaForm, PuntajeForm
from servicios.models import Actividad, Servicio, AdministradorServicio, \
    Opinion, Foto, TipoServicio, Puntaje, UbicacionComun

@csrf_exempt
def ser_inicio(request):
    """
    Muestra la página de inicio de servicios y procesa búsquedas de servicios,
    login de administradores de servicio y registro de nuevos servicios por
    parte de los usuarios
    """
    html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    captcha_error = None

    if request.method == "POST":
        if "login" in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['email'],
                                    password=login_form.cleaned_data['contrasena'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        admin = AdministradorServicio.objects.get(user=user)
                        request.session['django_language'] = admin.idioma
                        translation.activate(admin.idioma)

                        return HttpResponseRedirect(reverse("ser_perfil_privado"))
                    else:
                        login_form.errors["email"] = [_(u"Your user account has not been \
                                                        activated, check your e-mail")]
                else:
                    login_form.errors["email"] = [_(u"Your username or password is incorrect")]
            busqueda_form = BusquedaForm()
            nuevo_servicio_form = ServicioPublicoForm()
            ubicacion_form = UbicacionForm()
            recuperar_form = RecuperarForm()

        elif "nuevo_servicio" in request.POST:
            check_captcha = captcha.submit(
                request.POST['recaptcha_challenge_field'],
                request.POST['recaptcha_response_field'],
                settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
            if check_captcha.is_valid is False:
                captcha_error = _(u"Written words are incorrect")
            ###begin escape for django' tests
            if  settings.DEBUG == False and 'appTest' in request.POST:
                captcha_error = None
            ###end escape for django' tests
            nuevo_servicio_form = ServicioPublicoForm(request.POST, request.FILES)
            ubicacion_form = UbicacionForm(request.POST)
            if nuevo_servicio_form.is_valid() and ubicacion_form.is_valid() and not captcha_error:
                servicio = Servicio.save_form(nuevo_servicio_form,
                                              ubicacion_form, estado=u"A")

                Actividad.register(u"R", servicio)
                nuevo_servicio_form = ServicioPublicoForm()
                ubicacion_form = UbicacionForm()
            busqueda_form = BusquedaForm()
            login_form = LoginForm()
            recuperar_form = RecuperarForm()

        elif "recuperar" in request.POST:
            recuperar_form = RecuperarForm(request.POST)
            if recuperar_form.is_valid():
                try:
                    usuario = AdministradorServicio.objects.get(
                        user__email=recuperar_form.cleaned_data['email'])
                    sendHtmlMail("info@machu-picchu100.com",
                                 _(u"New password for Machu Picchu 100"),
                                 "ser_recuperar_mail_%s.html" % usuario.idioma,
                                  {"usuario": usuario,
                                   "password": make_password(),
                                   "sitio": Site.objects.get_current()},
                                 recuperar_form.cleaned_data['email'],
                                 path="servicios/email_templates/")
                except AdministradorServicio.DoesNotExist:
                    recuperar_form.errors["email"] = [_(u"The e-mail account does not \
                                                      belong to any registered manager")]
            login_form = LoginForm()
            nuevo_servicio_form = ServicioPublicoForm()
            ubicacion_form = UbicacionForm()
            busqueda_form = BusquedaForm()
    else:
        busqueda_form = BusquedaForm()
        login_form = LoginForm()
        nuevo_servicio_form = ServicioPublicoForm()
        ubicacion_form = UbicacionForm()
        recuperar_form = RecuperarForm()

    return direct_response(request, "servicios/ser_inicio.html",
                           {"busqueda_form": busqueda_form,
                            "login_form": login_form,
                            "nuevo_servicio_form": nuevo_servicio_form,
                            "html_captcha": html_captcha,
                            "captcha_error": captcha_error,
                            "ubicacion_form": ubicacion_form,
                            "recuperar_form": recuperar_form,
                            "actividades": get_paginated(request, Actividad.objects.all(), 5),
                            "destacados": Servicio.objects.filter(destacado=True).order_by('?')[:3],
                            "valorados": Servicio.objects.all().order_by('-puntuacion')[:3],
                            "ubicaciones_comunes": UbicacionComun.objects.all()})


def ser_cambio_password(request, clave_activacion, password):
    """
    Cambio de contraseña validada por el usuario mediante su mail al recuperar
    contraseña desde la página
    """
    admin = AdministradorServicio.objects.get(clave_activacion=clave_activacion)
    admin.set_password(password)

    return HttpResponseRedirect(reverse('ser_inicio'))


@csrf_exempt
def ser_registro(request):
    """
    Muestra el formulario de registro para un nuevo servicio, envía un email de
    confirmación al cliente para validar la cuenta
    """
    html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    ser_captcha_error = None
    
    if request.method == "POST":
        if request.POST['instance']:
            servicio_id = request.POST['instance']
            if AdministradorServicio.objects.filter(servicio__id=servicio_id).exists():
                return HttpResponseRedirect(reverse('ser_registro'))
            else:
                servicio_instance = Servicio.accepted.get(id=servicio_id)
                form_registro = ServicioPrivadoForm(request.POST, request.FILES,
                                                    instance=servicio_instance)
                form_ubicacion = UbicacionForm(request.POST,
                                               instance=servicio_instance.ubicacion)
        else:
            form_registro = ServicioPrivadoForm(request.POST, request.FILES)
            form_ubicacion = UbicacionForm(request.POST)
        check_captcha = captcha.submit(
            request.POST['recaptcha_challenge_field'],
            request.POST['recaptcha_response_field'],
            settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            ser_captcha_error = _(u"Written words are incorrect")
        ###begin escape for django' tests
        if  settings.DEBUG == False and 'appTest' in request.POST:
            ser_captcha_error = None
        ###end escape for django' tests            
        if form_registro.is_valid() and form_ubicacion.is_valid() and not ser_captcha_error:
            servicio = Servicio.save_form(form_registro, form_ubicacion)
            admin = AdministradorServicio.save_form(form_registro, servicio)
            sendHtmlMail("info@machu-picchu100.com",
                         _(u"Manager registration in MP100"),
                         "ser_regadmin_mail_%s.html" % admin.idioma,
                         {"nombre": servicio.nombre,
                          "sitio": Site.objects.get_current(),
                          "email": form_registro.cleaned_data['email']},
                         form_registro.cleaned_data['email'],
                         path="servicios/email_templates/")

            return direct_response(request, "servicios/ser_confirmacion.html")
    else:

        form_registro = ServicioPrivadoForm()
        form_ubicacion = UbicacionForm()

    return direct_response(request, "servicios/ser_registro.html",
                           {"form_registro": form_registro,
                            "form_ubicacion": form_ubicacion,
                            "html_captcha": html_captcha,
                            "ser_captcha_error": ser_captcha_error})


def ser_verificar_usuario(request, clave):
    """
    Coloca el estado del usuario como activo al acceder este a su correo y
    confirmar a travéz del link su cuenta
    """
    admin = get_object_or_404(AdministradorServicio, clave_activacion=clave)
    admin.set_active()

    return HttpResponseRedirect(reverse('ser_inicio'))


@login_required
def ser_cerrar_sesion(request):
    """
    logout para el administrador de servicio
    """
    logout(request)

    return HttpResponseRedirect(reverse('ser_inicio'))

FILTROS = {
    "puntuacion": _(u"Top ranked"),
    "num_opiniones": _(u"Most discussed"),
    "num_visitas": _(u"Most visited"),
}

@csrf_exempt
def ser_perfiles(request, filtro, id_tipo=None):
    """
    Muestra la página de resultados de una búsqueda, en caso de especificar
    un tipo de servicio se habilitará otra de las pestañas, los resultados serán
    paginados
    """
    if "busqueda" in request.session:
        busqueda = request.session["busqueda"]
    else:
        busqueda = {"direccion": _(u"all locations"), "tipo": None,
                    "latitud": "-16.3167", "longitud": "-71.55",
                    "filtro": "puntuacion"}

    if request.method == "POST":
        busqueda_form = BusquedaForm(request.POST)
        resultados = Servicio.accepted.all()
        if busqueda_form.is_valid():
            if busqueda_form.cleaned_data["ubicacion"]:
                if not busqueda_form.cleaned_data["location"]:
                    busqueda_form.errors["ubicacion"] = _(u"Your request cannot \
                        be processed if you don't enable javascript in your explorer")
                else:
                    (busqueda["latitud"], busqueda["longitud"]) = \
                        busqueda_form.cleaned_data['location'].split(",")
                    (lo_lat, lo_lng, hi_lat, hi_lng) = \
                        busqueda_form.cleaned_data['viewport'].split(",")
                    resultados = resultados.filter(
                        ubicacion__latitud__range=(lo_lat, hi_lat),
                        ubicacion__longitud__range=(lo_lng, hi_lng)
                    )
                    busqueda["direccion"] = busqueda_form.cleaned_data["ubicacion"]
            else:
                busqueda["direccion"] = _(u"all locations")
            request.session["resultados"] = resultados
            if busqueda_form.cleaned_data['tipo']:
                busqueda["tipo"] = busqueda_form.cleaned_data['tipo']
                resultados = resultados.filter(tipo_servicio=busqueda["tipo"])
            else:
                busqueda["tipo"] = None
            resultados = resultados.order_by("-%s" % filtro)
            request.session["busqueda"] = busqueda
    else:
        if "resultados" in request.session and id_tipo:
            resultados = request.session["resultados"]
        else:
            resultados = Servicio.accepted.all()

        if id_tipo:
            busqueda["tipo"] = get_object_or_404(TipoServicio, id=id_tipo)
            resultados = resultados.filter(tipo_servicio=busqueda["tipo"])
        else:
            busqueda["tipo"] = None

        busqueda["filtro"] = filtro
        resultados = resultados.order_by("-%s" % filtro)
        request.session["busqueda"] = busqueda
        busqueda_form = BusquedaForm()

    if resultados.filter(destacado=True).exists():
        destacado = resultados.filter(destacado=True).order_by("?")[0]
    else:
        destacado = None

    return direct_response(request, "servicios/ser_perfiles.html",
                           {"resultados": get_paginated(request, resultados, 4),
                            "all_results": resultados,
                            "tipos": TipoServicio.objects.all(),
                            "destacado": destacado,
                            "busqueda_form": busqueda_form,
                            "busqueda": busqueda,
                            "filtros": FILTROS})


@csrf_exempt
def ser_perfil_publico(request, id_servicio):
    """
    Muestra el perfil público de alguno de los servicios donde se puede puntuar
    el servicio y dejar opiniones
    """
    servicio = get_object_or_404(Servicio, id=id_servicio, estado=u"A")
    opiniones = Opinion.objects.filter(servicio=servicio, moderado=True)
    destacados = Servicio.accepted.filter(destacado=True).order_by("?")[:5]
    puntaje = Puntaje.get_or_none(servicio, request.user)
    comentado = False
    msg_enviado = False
    if request.method == "POST":
        if "opinion" in request.POST:
            opinion_form = OpinionForm(request.POST)
            puntuacion_form = PuntajeForm(request.POST, instance=puntaje)
            if opinion_form.is_valid() and puntuacion_form.is_valid() or not puntuacion_form:
                Opinion.save_form(opinion_form, servicio, request.user)
                Puntaje.save_form(puntuacion_form, servicio, request.user, puntaje)
                opinion_form = OpinionForm()
                puntuacion_form = PuntajeForm(instance=puntaje)
                request.user.get_profile().add_points(5)
            if AdministradorServicio.objects.filter(servicio=servicio).exists():
                contacto_form = ContactoForm()
            else:
                contacto_form = None
            comentado = True

        elif "contacto" in request.POST:
            contacto_form = ContactoForm(request.POST)
            if contacto_form.is_valid():
                sendHtmlMail("info@machu-picchu100.com",
                             u"You've received a contact request",
                             "ser_contacto_mail_%s.html" % servicio.administradorservicio.idioma,
                             {"datos": contacto_form.cleaned_data,
                              "nombre_sitio": Site.objects.get_current().domain,
                              "email": servicio.administradorservicio.user.email,},
                             servicio.administradorservicio.user.email,
                             path="servicios/email_templates/")
                msg_enviado = True
                contacto_form = ContactoForm()
                request.user.get_profile().add_points(5)
            opinion_form = OpinionForm()
            puntuacion_form = PuntajeForm()
    else:
        servicio.add_vista(request)
        opinion_form = OpinionForm()
        puntuacion_form = PuntajeForm(instance=puntaje)
        if AdministradorServicio.objects.filter(servicio=servicio).exists():
            contacto_form = ContactoForm()
        else:
            contacto_form = None

    return direct_response(request, "servicios/ser_perfil_publico.html",
                           {"servicio": servicio,
                            "galeria": Foto.objects.filter(servicio=servicio,
                                                           moderado=True),
                            "caracteristicas": servicio.caracteristicas.all(),
                            "opiniones": get_paginated(request, opiniones, 4),
                            "destacados": destacados,
                            "resultados": Servicio.get_search(request.session)[:3],
                            "opinion_form": opinion_form,
                            "puntuacion_form": puntuacion_form,
                            "contacto_form": contacto_form,
                            "msg_enviado": msg_enviado,
                            "comentado": comentado,
                            "fans": servicio.get_fans()})


@csrf_exempt
@login_required
@change_password
def ser_perfil_privado(request, **kwargs):
    """
    Muestra todos los datos del perfil de un servicio editables para su
    administrador, además la posibilidad de contestar opiniones sobre el
    servicio
    """
    admin = get_object_or_404(AdministradorServicio, user=request.user)
    servicio = admin.servicio
    opiniones = Opinion.objects.filter(servicio=servicio)
    if request.method == "POST" and not kwargs["cambio_form"].is_bound:
        ubicacion_form = UbicacionForm(request.POST, instance=servicio.ubicacion)
        servicio_form = ServicioEdicionForm(request.POST, instance=servicio)
        if ubicacion_form.is_valid() and servicio_form.is_valid():
            servicio.edit(servicio_form, ubicacion_form, request.session)
    else:
        ubicacion_form = UbicacionForm(instance=servicio.ubicacion)
        servicio_form = ServicioEdicionForm(instance=servicio)

    return direct_response(request, "servicios/privado/ser_perfil_privado.html",
                           {"servicio": servicio,
                            "opiniones": get_paginated(request, opiniones, 4),
                            "ubicacion_form": ubicacion_form,
                            "servicio_form": servicio_form,
                            "cambio_form": kwargs["cambio_form"]})


@login_required
@csrf_exempt
@change_password
def ser_editar_fotos(request, **kwargs):
    """
    Muestra un editor de las fotos cargadas al perfil así como un formulario
    para subir fotos nuevas
    """
    admin = get_object_or_404(AdministradorServicio, user=request.user)
    galeria = Foto.objects.filter(servicio=admin.servicio)
    if request.method == "POST" and not kwargs["cambio_form"].is_bound:
        if "guardar" in request.POST:
            guardar_form = FotoForm(request.POST, request.FILES)
            if guardar_form.is_valid():
                Foto.save_form(guardar_form, admin.servicio)
                guardar_form = FotoForm()
            editar_form = EditFotoForm(prefix="edit")
            panoramica_form = ServicioPanoramicaForm(instance=admin.servicio)

        elif "editar" in request.POST:
            foto = Foto.objects.get(id=request.POST["edit-id"])
            editar_form = EditFotoForm(request.POST, instance=foto,
                                       prefix="edit")
            if editar_form.is_valid():
                foto.edit(editar_form)
                editar_form = EditFotoForm(prefix="edit")
            guardar_form = FotoForm()
            panoramica_form = ServicioPanoramicaForm(instance=admin.servicio)

        elif "panoramica" in request.POST:
            panoramica_form = ServicioPanoramicaForm(request.POST, request.FILES,
                                                     instance=admin.servicio)
            if panoramica_form.is_valid():
                panoramica_form.save()
            guardar_form = FotoForm()
            editar_form = EditFotoForm(prefix="edit")

    else:
        panoramica_form = ServicioPanoramicaForm(instance=admin.servicio)
        guardar_form = FotoForm()
        editar_form = EditFotoForm(prefix="edit")

    return direct_response(request, "servicios/privado/ser_editar_fotos.html",
                           {"servicio": admin.servicio,
                            "galeria": galeria,
                            "panoramica_form": panoramica_form,
                            "guardar_form": guardar_form,
                            "editar_form": editar_form,
                            "cambio_form": kwargs["cambio_form"]})


@login_required
def ser_eliminar_foto(request, id_foto):
    """
    Borra una de las fotos del usuario
    """
    foto = get_object_or_404(Foto, id=id_foto)
    foto.delete()

    return HttpResponseRedirect(reverse('ser_editar_fotos'))


def json_fast_servicios(request, substring):
    """
    Búsqueda de una subcadena de texto dentro de los servicios
    """
    servicios = Servicio.accepted.all()

    return json_fastsearch(servicios, 'nombre', substring,
                           {"id": "id",
                            "name": "nombre",
                            "subtitle": "tipo_servicio",
                            "description": "descripcion",
                            "image": "foto_principal"})


def json_fast_noadmin(request, substring):
    """
    Búsqueda de una subcadena de texto dentro de los servicios
    """
    servicios = Servicio.accepted.filter(administradorservicio=None)

    return json_fastsearch(servicios, 'nombre', substring,
                           {"id": "id",
                            "name": "nombre",
                            "subtitle": "tipo_servicio",
                            "description": "descripcion",
                            "image": "foto_principal"})


def json_get_servicio(request, servicio_id):
    """
    Devuelve los datos de un servicio
    """
    servicio = get_object_or_404(Servicio, id=servicio_id, estado=u"A")
    json_dict = {"id": servicio.id,
                 "nombre": servicio.nombre,
                 "tipo": servicio.tipo_servicio.id,
                 "direccion": servicio.ubicacion.direccion,
                 "latitud": servicio.ubicacion.latitud,
                 "longitud": servicio.ubicacion.longitud}

    return json_response(json_dict)


@login_required
def json_valorar_opinion(request, opinion_id):
    """
    Una opinión recibe la valoración de un usuario
    """
    opinion = get_object_or_404(Opinion, id=opinion_id)
    data = {"nuevo": opinion.add_valoracion(request.user)}

    return json_response(data)


@login_required
def json_responder_opinion(request, opinion_id, respuesta):
    """
    Una opinión recibe la respuesta del administrador
    """
    opinion = get_object_or_404(Opinion, id=opinion_id)
    admin = get_object_or_404(AdministradorServicio, user=request.user)
    verified = opinion.set_respuesta(admin, respuesta)
    data = {"verified": verified}

    return json_response(data)


def json_get_panimage(request, index):
    """
    Devuelve una imágen panorámica de los servicios
    """
    servicios = Servicio.accepted.filter(destacado=True)
    if servicios:
        servicio = servicios[(int(index)+1)%len(servicios)]
        data = {
            "img": servicio.foto_panoramica.generate_url("pano"),
            "des": "%s ..." % servicio.descripcion[:74],
            "url": servicio.get_absolute_url(),
        }

        return json_response(data)
    else:
        return json_response({})
