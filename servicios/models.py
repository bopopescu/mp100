# -*- coding: utf-8 -*-

from datetime import datetime
import random
import sha
from common.utils import sendHtmlMail, get_object_or_none
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from django.conf import settings
from MP100.athumb.fields import ImageWithThumbsField
from common.validators import validate_phone
from fotos.models import UserProfile
from MP100.athumb.backends.s3boto import S3BotoStorage_AllPublic
PUBLIC_MEDIA_BUCKET = S3BotoStorage_AllPublic(settings.AWS_STORAGE_BUCKET_NAME)


class ThumbBase(models.Model):
    """
    Base para incluir una ImageWithThumbsField
    """
    height = models.IntegerField(null=True)
    width = models.IntegerField(null=True)

    class Meta:
        abstract = True


class Ubicacion(models.Model):
    """
    Una ubicación global considerando la latitud y la longitud
    """
    direccion = models.CharField(max_length=300, verbose_name=u"address")
    latitud = models.FloatField(verbose_name=_("latitude"))
    longitud = models.FloatField(verbose_name=_("longitude"))

    def __unicode__(self):
        return u"%s" % self.direccion

    def get_map(self):
        """
        Retorna la ubicación del servicio en el mapa
        """
        return u"<img src='http://maps.google.com/staticmap?center=%s&markers=%s,blues&zoom=14&size=200x200&sensor=false'/>" % (self.getLatLng(), self.getLatLng())

    get_map.short_description = _(u"location")
    get_map.allow_tags = True

    def getLatLng(self):
        """
        Devuelve la latitud y longitud de la ubicación
        """
        return "%s,%s" % (self.latitud, self.longitud)

    class Meta:
        verbose_name = _(u"location")
        verbose_name_plural = _(u"locations")


class TipoServicio(ThumbBase):
    """
    Tipo de servicio general
    """
    nombre = models.CharField(max_length=30, verbose_name=_(u"name"))
    icono = ImageWithThumbsField(
        _(u'icon'),
        upload_to="servicios/iconos_ser",
        thumbnail_format='png',
        width_field='width', height_field='height',
        storage=PUBLIC_MEDIA_BUCKET,
        thumbs=(
            ('small', {'size': (20, 20), 'crop':'center', 'upscale':True}),
        )
    )

    def __unicode__(self):
        return u"%s" % self.nombre

    def get_icono(self):
        """
        Devuelve el ícono del tipo de servicio para mostrarlo en la página de
        administración
        """
        return u"<img src='%s' />" % self.icono.generate_url("small")

    get_icono.short_description = _(u"icon")
    get_icono.allow_tags = True

    class Meta:
        verbose_name = _(u"type of service")
        verbose_name_plural = _(u"types of services")


class SubtipoServicio(models.Model):
    """
    Tipo dentro de un tipo de servicio
    """
    nombre = models.CharField(max_length=30, verbose_name=_(u"name"))
    tipo_servicio = models.ForeignKey(TipoServicio,
                                      verbose_name=_(u"type of service"))

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name = _(u"subtype of service")
        verbose_name_plural = _(u"subtype of services")


class Caracteristica(ThumbBase):
    """
    Característica iconizada de un tipo de servicio
    """
    nombre = models.CharField(max_length=40, verbose_name=_(u"name"))
    icono = ImageWithThumbsField(
        _(u'icon'),
        upload_to="servicios/iconos_ser",
        thumbnail_format='png',
        width_field='width', height_field='height',
        blank=True, null=True,
        storage=PUBLIC_MEDIA_BUCKET,
        thumbs=(
            ('small', {'size': (20, 20), 'crop':'center', 'upscale':True}),
        )
    )
    tipo_servicio = models.ForeignKey(TipoServicio,
                                      verbose_name=_(u"type of service"))

    def __unicode__(self):
        return u"%s" % self.nombre

    def get_icono(self):
        """
        Devuelve el ícono de la característica para mostrarlo en la página de
        administración
        """
        if self.icono:
            return u"<img src='%s' />" % self.icono.generate_url("small")
        else:
            return u""

    get_icono.short_description = _("icon")
    get_icono.allow_tags = True

    class Meta:
        verbose_name = _(u"feature")
        verbose_name_plural = _(u"features")


class ServicioManager(models.Manager):
    """
    Object manager para los servicios, devuelve a los que tienen estado aceptado
    """
    def get_query_set(self):
        return super(ServicioManager, self).get_query_set().filter(estado=u"A")


class Servicio(ThumbBase):
    """
    Representa un servicio de cualquier categoría
    """
    nombre = models.CharField(_(u"name"), max_length=150)
    tipo_servicio = models.ForeignKey(TipoServicio,
                                      verbose_name=_(u"type of service"))
    subtipo_servicio = models.ForeignKey(SubtipoServicio,
                                         verbose_name=_(u"subtype of service"),
                                         blank=True, null=True)
    descripcion = models.TextField(verbose_name=_(u"description"), blank=True,
                                   null=True, default=u"")
    foto_principal = ImageWithThumbsField(
        _(u'main photo'),
        upload_to="servicios/fotos",
        width_field='width', height_field='height',
        storage=PUBLIC_MEDIA_BUCKET, thumbnail_format='jpeg',
        thumbs=(
            ('icon', {'size': (35, 30), 'crop':'center', 'upscale':True}),
            ('bigIcon', {'size': (50, 50), 'crop':'center', 'upscale':True}),
            ('preview', {'size': (70, 63), 'crop':'center', 'upscale':True}),
            ('edit', {'size': (152, 162), 'crop':'center', 'upscale':True}),
            ('gallery', {'size': (443, 250), 'crop':'center', 'upscale':True}),
        )
    )
    height_p = models.IntegerField(null=True)
    width_p = models.IntegerField(null=True)
    foto_panoramica = ImageWithThumbsField(
        _(u'panoramic photo'),
        upload_to="servicios/fotos",
        width_field='width_p', height_field='height_p',
        storage=PUBLIC_MEDIA_BUCKET, thumbnail_format='jpeg',
        blank=True, null=True,
        help_text=_(u"The picture you load here will be used to have advertising on our home page, it must be at least 975px width and 376px height to be accepted"),
        thumbs=(
            ('pano', {'size': (975, 376), 'crop':'center', 'upscale':True}),
            ('preview', {'size': (190, 80), 'crop':'center', 'upscale':True}),
        )
    )
    ESTADO_CHOICES = (
        (u"E", _(u"Waiting")),
        (u"A", _(u"Accepted")),
        (u"R", _(u"Rejected")),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES,
                              default=u"E", verbose_name=_(u"state"))
    ubicacion = models.ForeignKey(Ubicacion, verbose_name=_(u"location"))
    telefono = models.CharField(max_length=11,
                                validators=[validate_phone],
                                verbose_name=_(u"phone"),
                                blank=True, null=True)
    caracteristicas = models.ManyToManyField(Caracteristica,
                                             verbose_name=_(u"features"),
                                             blank=True, null=True)
    puntuacion = models.FloatField(verbose_name=_(u"score"), default=0)
    website = models.URLField(blank=True, null=True)
    num_visitas = models.IntegerField(_(u"visits"),
                                      default=0)
    num_opiniones = models.IntegerField(_(u"reviews"),
                                        default=0)
    num_puntuaciones = models.IntegerField(_(u"scores"),
                                           default=0)
    destacado = models.BooleanField(_(u"promoted"), default=False)
    # managers
    objects = models.Manager()
    accepted = ServicioManager()

    def __unicode__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        """
        Método para guardar un servicio, cuando este es moderado se manda el
        correo electrónico de confirmación
        """
        if self.estado == u"A":
            admin = get_object_or_none(AdministradorServicio, servicio=self)
            if admin:
                sendHtmlMail("info@machu-picchu100.com",
                             _(u"Confirm registration in MP100"),
                             "ser_confirmacion_mail_%s.html" % admin.idioma,
                             {"nombre": self.nombre,
                              "clave": admin.clave_activacion,
                              "sitio": Site.objects.get_current(),
                              "email": admin.user.email},
                             admin.user.email,
                             path="servicios/email_templates/")

        super(Servicio, self).save(*args, **kwargs)

        if self.estado == u"R":
            Servicio.objects.get(id=self.id).delete()

    def delete(self, using=None):
        """
        Borra al administrador del servicio, las actividades, fotos, puntajes y
        opiniones,
        """
        Foto.objects.filter(servicio=self).delete()
        Puntaje.objects.filter(servicio=self).delete()
        Opinion.objects.filter(servicio=self).delete()
        Actividad.objects.filter(servicio=self).delete()
        self.ubicacion.delete()

        return super(Servicio, self).delete(using)

    def get_foto(self):
        """
        Retorna la foto principal del servicio para la página de administración
        """
        return u"<img src='%s' />" % self.foto_principal.generate_url("edit")

    get_foto.short_description = _(u"main photo")
    get_foto.allow_tags = True

    def get_ubicacion(self):
        """
        Retorna la ubicación del servicio en el mapa
        """
        return u"<img src='http://maps.google.com/staticmap?center=%s&markers=%s,blues&zoom=14&size=200x200&sensor=false'/>" % (self.ubicacion.getLatLng(), self.ubicacion.getLatLng())

    get_ubicacion.short_description = _(u"location")
    get_ubicacion.allow_tags = True

    def get_act_str(self):
        """
        Retorna el html de su activity stream 
        """
        _url = self.get_absolute_url()
        if get_language() == 'en':
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">The service <a href="%s">%s</a> has just registered successfully. <a href="%s">See More</a></div></div>' % (_url,self.foto_principal.generate_url('bigIcon'.strip()),_url,self.nombre,_url)
        else:
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">El servicio <a href="%s">%s</a> se ha registrado con éxito. <a href="%s">Ver más</a></div></div>' % (_url,self.foto_principal.generate_url('bigIcon'.strip()),_url,self.nombre,_url)
 
    get_act_str.allow_tags=True

    def get_fans(self, num=3):
        """
        Obtiene los fans de un servicio, son lo que dejaron un puntaje mayor a 3
        """
        puntajes = Puntaje.objects.filter(servicio=self, puntuacion__gt=3)
        fans = puntajes.values("usuario").order_by().distinct()[:num]

        return [UserProfile.objects.get(id=id["usuario"]) for id in fans]

    @staticmethod
    def save_form(servicio_form, ubicacion_form, estado=u"E"):
        """
        Crea un nuevo servicio a partir de formularios para servicio y ubicación
        """
        servicio = servicio_form.save(commit=False)
        servicio.ubicacion = ubicacion_form.save()
        servicio.estado = estado
        servicio.save()
        foto = Foto(nombre=servicio.nombre, servicio=servicio,
                    imagen=servicio.foto_principal)
        foto.save()

        return servicio

    @staticmethod
    def get_search(session):
        """
        Si se realizó una búsqueda se devuelve el resultado, sino se devuelven
        todos los servicios
        """
        if "resultados" in session:
            return session["resultados"]
        else:
            return Servicio.accepted.all()

    def edit(self, servicio_form, ubicacion_form, session):
        """
        Modifica el objeto según los datos ingresados en lso formularios de servicio
        y ubicación, además registra la actividad una vez dependiendo de una variable
        de sesión
        """
        ubicacion_form.save()
        servicio_form.save()
        if 'editado' in session:
            session['editado'] = False
        else:
            session['editado'] = True
            session.set_expiry(0)
            Actividad.register(u"P", self)

    def add_vista(self, request):
        """
        Incrementa una vista al servicio
        """
        if request.user.is_authenticated() and \
           AdministradorServicio.objects.filter(user=request.user).exists():
            servicio = Servicio.objects.get(administradorservicio__user=request.user)
        else:
            servicio = None
            
        if self != servicio:
            if 'vista_ser_%s' % self.id in request.session:
                request.session['vista_ser_%s' % self.id] = False
            else:
                request.session['vista_ser_%s' % self.id] = True
                request.session.set_expiry(43200)
                self.num_visitas += 1
                self.save()

    def set_nueva_opinion(self):
        """
        Aumenta el contador de opiniones
        """
        self.num_opiniones += 1
        self.save()

    def set_nueva_puntuacion(self, nuevo, antiguo=None):
        """
        Calcula la nueva puntuación
        """
        if antiguo:
            self.puntuacion = self.puntuacion + (self.puntuacion - antiguo)/self.num_puntuaciones
        else:
            self.num_puntuaciones += 1
        self.puntuacion = self.puntuacion - (self.puntuacion - nuevo)/self.num_puntuaciones
        self.save()

    @models.permalink
    def get_absolute_url(self):
        return 'servicios.views.ser_perfil_publico', [str(self.id)]

    class Meta:
        unique_together = ("nombre", "tipo_servicio", "ubicacion")
        verbose_name = _(u"service")
        verbose_name_plural = _(u"services")
    

class AdministradorServicio(models.Model):
    """
    Administrador de un servicio
    """
    user = models.OneToOneField(User, unique=True, related_name="service_admin")
    servicio = models.OneToOneField(Servicio, verbose_name=_(u"service"))
    clave_activacion = models.CharField(max_length=40,
                                        verbose_name=_(u"activation key"))
    LANGUAGE_CHOICES = (
        (u"en", u"English"),
        (u"es", u"Spanish")
    )
    idioma = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,
                              default=u'es')

    def __unicode__(self):
        return u"%s" % self.servicio

    def delete(self, using=None):
        """
        Borra las respuestas hechas por el administrador sobre las opiniones de
        de su servicio
        """
        self.user.delete()
        Respuesta.objects.filter(administrador=self).delete()

        return super(AdministradorServicio, self).delete(using)

    @staticmethod
    def save_form(form, servicio):
        """
        Crea un nuevo administrador de servicio a partir del formulario de registro
        de un nuevo servicio
        """
        email = form.cleaned_data['email']
        user = User.objects.create_user(email, email,
                                        form.cleaned_data['contrasenia'])
        user.is_active = False
        user.save()
        user = User.objects.get(id=user.id)
        salt = sha.new(str(random.random())).hexdigest()[:5]
        clave_activacion = sha.new(salt+user.email).hexdigest()
        admin_servicio = AdministradorServicio(user=user,
                                               servicio=servicio,
                                               clave_activacion=clave_activacion)
        admin_servicio.save()
        
        return admin_servicio

    def set_password(self, password):
        """
        Cambia el password del usuario asignado al administrador de servicio
        """
        self.user.set_password(password)
        self.user.save()

    def set_active(self):
        """
        Cambia el estado del usuario asignado al administrador de servicio a
        activo y registra la actividad relacionada
        """
        if not self.user.is_active:
            self.user.is_active = True
            self.user.save()
            Actividad.register(u"A", self.servicio)

    class Meta:
        verbose_name = _(u"service manager")
        verbose_name_plural = _(u"service managers")


class Respuesta(models.Model):
    """
    La respuesta de un administrador de servicio sobre una opinión hecha por
    alguno de los usuarios
    """
    texto = models.TextField(_(u"text"))
    administrador = models.ForeignKey(AdministradorServicio,
                                      verbose_name=_(u"service manager"))

    def __unicode__(self):
        return u"%s: %s" % (self.administrador, self.texto)

    class Meta:
        verbose_name = _(u"reply")
        verbose_name_plural = _(u"replies")


class Opinion(models.Model):
    """
    Una opinión de un usuario sobre un servicio, las opiniones contienen una
    puntuación sobre el servicio donde se realizó y una valoración de otros
    usuarios sobre esta opinión
    """
    usuario = models.ForeignKey(UserProfile, verbose_name=_(u"user"))
    servicio = models.ForeignKey(Servicio, verbose_name=_(u"service"))
    texto = models.TextField(_(u"text"))
    valoracion = models.IntegerField(_(u"valuation"), default=0)
    fecha = models.DateTimeField(_(u"date"), default=datetime.now)
    moderado = models.BooleanField(_(u"moderate"), default=False)
    respuesta = models.OneToOneField(Respuesta, blank=True, null=True,
                                     verbose_name=_(u"reply"))
    fans = models.ManyToManyField(User, verbose_name=_(u"fans"))

    def __unicode__(self):
        return u"%s -> %s" % (self.usuario, self.servicio)

    def save(self, *args, **kwargs):
        """
        Cuando la opinión ha sido moderada se cambia la puntuación del
        servicio donde se realizó y se registra la actividad relacionada
        """
        if self.moderado:
            self.servicio.set_nueva_opinion()
            Actividad.register(u"O", self.servicio, self.usuario)
        
        return super(Opinion, self).save(*args, **kwargs)

    @staticmethod
    def save_form(form, servicio, user):
        """
        Crea una nueva opinion en base a un formulario
        """
        opinion = form.save(commit=False)
        opinion.servicio = servicio
        opinion.usuario = get_object_or_404(UserProfile, user=user)
        opinion.save()

    def add_valoracion(self, fan):
        """
        Añade una valoración a la opinión
        """
        if not fan in self.fans.all():
            self.fans.add(fan)
            self.valoracion += 1
            self.save()

        return self.valoracion

    def set_respuesta(self, admin, texto):
        """
        Establece la respuesta de un administrador de servicio para esta
        opinión
        """
        if self.servicio == admin.servicio:
            respuesta = Respuesta(texto=texto, administrador=admin)
            respuesta.save()
            self.respuesta = respuesta
            self.save()
            Actividad.register(u"E", self.servicio, self.usuario)
            return True
        else:
            return False

    class Meta:
        ordering  = ["-fecha"]
        verbose_name = _(u"review")
        verbose_name_plural = _(u"reviews")
        

class Puntaje(models.Model):
    """
    Puntuación de un usuario sobre un servicio, sólo una puntuación de
    cada usuario por servicio
    """
    usuario = models.ForeignKey(UserProfile, verbose_name=_(u"user"))
    servicio = models.ForeignKey(Servicio, verbose_name=_(u"service"))
    puntuacion = models.IntegerField(
        verbose_name=_(u"score"),
        help_text=_(u"You can change your score to this service")
    )

    def save(self, puntaje=None, *args, **kwargs):
        """
        La puntuación nueva debe alterar el puntaje del servicio
        """
        if puntaje:
            self.servicio.set_nueva_puntuacion(self.puntuacion, puntaje.puntuacion)
        else:
            self.servicio.set_nueva_puntuacion(self.puntuacion)

        return super(Puntaje, self).save(*args, **kwargs)

    @staticmethod
    def save_form(form, servicio, user, puntaje):
        """
        Crea una nueva puntuación en base a un formulario
        """
        puntuacion = form.save(commit=False)
        puntuacion.servicio = servicio
        puntuacion.usuario = get_object_or_404(UserProfile, user=user)
        puntuacion.save(puntaje)

    @staticmethod
    def get_or_none(servicio, usuario):
        """
        Devuelve el objeto puntaje o None
        """
        if usuario.is_authenticated():
            try:
                return Puntaje.objects.get(servicio=servicio, usuario=usuario)
            except Puntaje.DoesNotExist:
                return None
        else:
            return None

    class Meta:
        unique_together = ("usuario", "servicio")
        verbose_name = _(u"score")
        verbose_name_plural = _(u"scores")


class Foto(ThumbBase):
    """
    Foto de la galería de un servicio
    """
    nombre = models.CharField(_(u"name"), max_length=50)
    servicio = models.ForeignKey(Servicio, verbose_name=_(u"service"))
    imagen = ImageWithThumbsField(
        _(u'picture'),
        upload_to="servicios/fotos",
        width_field='width', height_field='height',
        storage=PUBLIC_MEDIA_BUCKET, thumbnail_format='jpeg',
        thumbs=(
            ('icon', {'size': (35, 30), 'crop':'center', 'upscale':True}),
            ('preview', {'size': (70, 63), 'crop':'center', 'upscale':True}),
            ('edit', {'size': (152, 162), 'crop':'center', 'upscale':True}),
            ('gallery', {'size': (443, 250), 'crop':'center', 'upscale':True}),
        )
    )
    descripcion = models.TextField(_(u"description"),
                                   blank=True, null=True,
                                   default=u"")
    moderado = models.BooleanField(_(u"moderate"), default=False)

    def __unicode__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        """
        Cuando el estado cambia a moderado se registra la actividad
        """
        if self.moderado:
            Actividad.register(u"F", self.servicio)

        return super(Foto, self).save(*args, **kwargs)

    def get_imagen(self):
        """
        Devuelve el ícono de la característica para mostrarlo en la página de
        administración
        """

        return u"<img src='%s' />" % self.imagen.generate_url("edit")

    get_imagen.short_description = _(u"picture")
    get_imagen.allow_tags = True

    @staticmethod
    def save_form(form, servicio):
        """
        Guarda una nueva foto usando un FotoForm, registra la actividad y si se
        trata de una foto principal la guarda en el servicio
        """
        foto = form.save(commit=False)
        foto.servicio = servicio
        foto.save()
        if form.cleaned_data['principal']:
            servicio.foto_principal = foto.imagen
            servicio.save()

    def edit(self, form):
        """
        Edita algunos campos de una foto
        """
        form.save()
        if form.cleaned_data['principal']:
            self.servicio.foto_principal = self.imagen
            self.servicio.save()

    class Meta:
        verbose_name = _(u"photo")
        verbose_name_plural = _(u"photos")


class Actividad(models.Model):
    """
    Actividad realizada por un usuario
    """
    ACTIVIDAD_CHOICES = (
        # Nuevo servicio registrado sin administrador
        (u'R', _(u'is registered now')),
        # Nuevo servicio administrado
        (u'A', _(u'is registered now by an adminitrator')),
        # Nueva foto de un servicio
        (u'F', _(u'has uploaded a new photo')),
        # Comentario de un usuario en un servicio
        (u'O', _(u'received an opinion from')),
        # Respuesta de un administrador a un comentario
        (u'E', _(u'has answered an opinion made by')),
        # Cambio en los datos de un perfil
        (u'P', _(u'updated its profile')),
    )

    tipo = models.CharField(_(u"type"), max_length=1,
                            choices=ACTIVIDAD_CHOICES)
    fecha = models.DateTimeField(_(u"date"), default=datetime.now)
    servicio = models.ForeignKey(Servicio, verbose_name=_(u"service"))
    usuario = models.ForeignKey(UserProfile, blank=True, null=True,
                                verbose_name=_(u"user"))

    class Meta:
        ordering = ['-fecha']
        verbose_name = _(u"activity")
        verbose_name_plural = _(u"activities")

    @staticmethod
    def register(tipo, servicio, usuario=None):
        new = Actividad(tipo=tipo, servicio=servicio)
        if usuario:
            new.usuario = usuario
        new.save()

    def get_str(self):
        """
        Devuelve una cadena de texto representando la actividad
        """
        if self.usuario:
            usuario = self.usuario
        else:
            usuario = u""

        return u"%s %s %s %s" % (self.servicio.tipo_servicio, self.servicio,
                                 self.get_tipo_display(), usuario)

    get_str.short_description = _(u"Text")


class UbicacionComun(models.Model):
    """
    Lista de ubicaciones comunes para una búsqueda rápida
    """
    nombre = models.CharField(_(u"name"), max_length=100)
    ubicacion = models.CharField(_(u"location"), max_length=200)

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name = _(u"common location")
        verbose_name_plural = _(u"common locations")
