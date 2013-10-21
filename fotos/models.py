# -*- coding: utf-8 -*-
from signals import create_profile
from django.shortcuts import get_object_or_404
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from MP100.countries.models import Country
from MP100.common.utils import sendHtmlMail
from MP100.common.models import Departamento
from brabeion import badges
from brabeion.base import Badge, BadgeAwarded
#ACTIVAR SOLO EN EL SERVER
from MP100.fotos.tasks import startTemporada, closeTemporada
from datetime import datetime, timedelta
from django.db.models.signals import pre_save
from base64 import urlsafe_b64encode
from math import ceil
import os
import random
from MP100.athumb.fields import ImageWithThumbsField
from MP100.athumb.backends.s3boto import S3BotoStorage_AllPublic
PUBLIC_MEDIA_BUCKET = S3BotoStorage_AllPublic(settings.AWS_STORAGE_BUCKET_NAME)


class Categoria(models.Model):
    """
    Datos de una categoria de foto
    en ingles y espaniol
    """
    nombre = models.CharField(max_length = 100)
    nombre_espaniol = models.CharField(max_length = 100)
    descripcion = models.TextField(u'descripción', max_length = 250)
    descripcion_espaniol = models.TextField(u'descripción_espaniol',
                                            max_length = 250)

    def __unicode__(self):
        return u'%s' % self.nombre
  
class Temporada(models.Model):
    """
    Datos de las temporadas
    """
    fecha_inicio = models.DateTimeField(unique=True)
    fecha_fin = models.DateTimeField(unique=True)
    titulo = models.CharField(u'Título', max_length = 50, unique=True)
    descripcion =models.TextField(u'descripción', max_length = 250, blank=True)
    max_fotos_per_user = models.IntegerField(default=5)
    ganadores_por_votos = models.ManyToManyField(User, through='Ganador_Votos')

    def __unicode__(self):
        return u'%s' % self.titulo
    
    def get_max_fotos_per_user(self):
        """
        retorna el número de fotos por usuario para la temporada
        """
        return int(self.max_fotos_per_user)
        
    def is_close_yesterday(self):
        """
        Devuelve si la temporada acaba de temrinar para el cron job
        """
        difference = self.fecha_fin - datetime.now()
        return difference.days == 1
        
    def is_in_this_temporada(self, fecha):
        """
        Verifica si una fecha esta dentro de la temporada
        """
        return fecha >= self.fecha_inicio and fecha < self.fecha_fin
      
    def get_current_temporada(self):
        """
        el nombre esta mal, deberia ser get_actual_or_closest_temporada
        verifica si actualmente se esta dentro de una temporada
        si es asi la retorna, sino verifica la temporada mas proxima
        y la retorna
        si no hay temporadas o no hay temporadas posteriores a la
        fecha actual, retorna ''
        """
        now = datetime.now()
        currents = Temporada.objects.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now).order_by('fecha_inicio')
        if currents:
            return currents[0]
        futures = Temporada.objects.filter(
            fecha_inicio__gte=now,
            fecha_fin__gte=now).order_by('fecha_inicio')
        if futures:
            return futures[0]
        return ''

    def get_Current_Voting_Temporada(self):
        """
        si una temporada está actualmente en proceso de votación la retorna
        en caso contrario retorna ''
        """
        Current = Temporada().get_current_temporada()
        if Current and Current.is_in_this_temporada(datetime.now()):
                return Current
        return ''                
    
    def get_temporada_for(self, fecha):
        """
        Devuelve la temporada a la q corresponde una fecha
        sino no hay ninguna, retorna ""
        """
        closest_temp = ""
        lista_temporadas = Temporada.objects.all()
        if lista_temporadas:
            for temporada in lista_temporadas:
                if fecha < temporada.fecha_inicio:
                    if closest_temp:
                        if closest_temp.fecha_inicio > temporada.fecha_inicio:
                            closest_temp = temporada
                    else:
                        closest_temp = temporada
        return closest_temp
        
    
    # TODO: Pero hay que hacer una query para acceder a este método :/
    # no es static
    def get_last_temporada(self):
        """
        busca la ultima temporada que ha pasado y la retorna
        si no hay temporadas o temporadas pasadas retorna ""
        """
        now = datetime.now()
        closest_temp = ""
        lista_temporadas = Temporada.objects.all()
        if lista_temporadas:
            for temporada in lista_temporadas:
                if now > temporada.fecha_fin:
                    if closest_temp:
                        if closest_temp.fecha_fin < temporada.fecha_fin:
                            closest_temp = temporada
                    else:
                        closest_temp = temporada
        return closest_temp
    
    def get_all_foto_winners(self):
        """
        retorna una lista de todas las fotos que han sido ganadoras de alguna
        temporada
        """
        lista_temporadas  = Temporada.objects.all()
        lista_fotos = []
        if lista_temporadas:
            for temporada in lista_temporadas:
                lista_fotos.extend(temporada.foto_set.all())
        return lista_fotos

    def get_winners_from(self, temporada=0):
        """
        retorna una lista con los ganadores por sorteo
        de la temporada 'temporada'
        sino recibe un argumento retorna los ganadores de la
        misma temporada usada para llamar a esta función
        """
        if not temporada:
            temporada=self
        return [u.user for u in temporada.ganador_votos_set.all()]

    def get_next_temporada(self):
        """
        Retorna la temporada mas proxima a empezar,
        en caso no halla alguna, retorna ''
        """
        Current = Temporada().get_current_temporada()
        if Current:
            if not Current.is_in_this_temporada(datetime.now()):
                return Current
            return Temporada().get_temporada_for(Current.fecha_fin)
        return ''

    def get_order_number(self):
        """
        Retorna el número de temporada
        """
        return Temporada.objects.filter(fecha_inicio__lt=\
                                        self.fecha_inicio).count() + 1
        
    def get_contestants(self):
        """
        retorna un queryset con todos los concursantes que pudieron votar en
        esta temporada
        """
        return User.objects.filter(date_joined__lt=self.fecha_fin)
        
    def get_very_last_temporada(self):
        """
        Retorna la ultima temporada segun su fecha_fin
        si no hay ninguna temporada retorna []
        """
        last_temp = Temporada.objects.order_by('-fecha_fin')
        if last_temp:
            last_temp = last_temp[0]
        return last_temp

    def actualTemp_is_the_last_temporada(self):
        """
        retorna True si se está en la última temporada,
        en caso contrario retorna False
        """
        very_last_temporada = Temporada().get_very_last_temporada()
        if very_last_temporada:
            return very_last_temporada.is_in_this_temporada(datetime.now())
        return False

    def all_VotingPeriods_has_passed(self):
        """
        Retorna True si ya pasaron todos lo periodos de votación
        en caso contrario retorna False
        """
        very_last_temporada = Temporada().get_very_last_temporada()
        if very_last_temporada:
            if very_last_temporada.fecha_fin <= datetime.now():
                return True
        return False

    def get_start_receiving_date(self):
        """
        retorna la fecha en que inicia la recepción de fotos para este
        periodo de votación
        en caso no se hayan creado periodos de votación retorna ""
        si es el 1er periodo, retorna la fecha en que se creo el admin
        (osea la fecha de instalación del programa)
        """
        temp_list = Temporada.objects.order_by("id")
        if temp_list:
            temp_list=temp_list.filter(fecha_inicio__lt=self.fecha_inicio)
            temp_diff = ""
            
            for temp in temp_list:
                diff = self.fecha_inicio-temp.fecha_inicio
                if temp_diff == "":
                    temp_diff = diff
                if diff < temp_diff:
                    temp_diff = diff
                    temp_id = temp.id
            
            if temp_diff == "":
                return User.objects.get(id=1).date_joined
            else:
                return temp.fecha_inicio
        else:
            return ""
    
def register_jobs_temporada(sender, instance, **kwargs):
    """ sender: modelo de la clase
        instance: instancia siendo grabada
        using: el aleas de la DB
    registra en celery los taks de inicio y fin de temporada
    antes que sea grabado el nuevo registro de la temporada
    """
    
    temporada = instance
    #como no se permiten 2 temporadas con las mismas fecha_inicio y fecha_fin
    #si encuentra una entonces esta actualizando una temporada
    #si no la encuentra entonces esta creando una nueva temporada
    #y hay que crearle sus cronjobs

    if Temporada.objects.filter(fecha_inicio=temporada.fecha_inicio):
        a=1
    else:
        a=1
        startTemporada.apply_async(eta=temporada.fecha_inicio)
        #ese script de fin de temporada empieza un segundo después de la fecha
        #de termino porque siempre evalua la ultima temporada pasada
        closeTemporada.apply_async(eta=temporada.fecha_fin+timedelta(0,1))
        #ACTIVAR ESTO SOLO EN UNIX (SOLO SI SE USARAN CRONJOBS EN LUDAR DE
        #CELERY)
        #commands_path=os.path.join(settings.BASEDIR, 'manage.py')
        #dow = temporada.fecha_inicio.weekday() + 1 #comienza con 0 en lunes pero se requiere con 0 en domingo
        #if dow == 7:
        #    dow = 0
        #os.system('(echo "1992" | sudo -S login giussepi; echo "1992" | sudo crontab -l; echo "%s %s %s %s %s sudo python %s start_temporada") | sudo crontab -' % (temporada.fecha_inicio.minute, temporada.fecha_inicio.hour, temporada.fecha_inicio.day, temporada.fecha_inicio.month, dow, commands_path))
        #dow = temporada.fecha_fin.weekday() + 1 #comienza con 0 en lunes pero se requiere con 0 en domingo
        #if dow == 7:
        #    dow = 0
        #os.system('(echo "1992" | sudo -S login giussepi; echo "1992" | sudo -S crontab -l; echo "%s %s %s %s %s sleep 1 && sudo python %s close_temporada") | sudo crontab -' % (temporada.fecha_fin.minute, temporada.fecha_fin.hour, temporada.fecha_fin.day, temporada.fecha_fin.month, dow, commands_path))

pre_save.connect(register_jobs_temporada, sender=Temporada)

class Ganador_Votos(models.Model):
    """
    Alamacena los ganadores por sorteo
    """
    user = models.ForeignKey(User)
    temporada = models.ForeignKey(Temporada)
    #num_votos = models.IntegerField()

class AliveFotoManager(models.Manager):
    """
    DEvuelve todas las fotos con estado alive
    """
    def get_query_set(self):
        return super(AliveFotoManager, self).get_query_set().filter(alive=True)

def size_validator(photo):
    """
    La foto no debe ser mayor a 5Mb
    """
    if photo.size > 5000000:
        raise ValidationError(_(u"Your photo must not be larger than 5 megabytes in size."))


class Foto(models.Model):
    """
    Datos de una foto
    """
    ESTADO_CHOICES = (
        (u"M", u"Moderado"),
        (u"E", u"Espera"),
        (u"R", u"Rechazada"),
    )
    HABILITADO_CHOICES = (
        (u"N", u"N"),
        (u"S", u"SI"),
    )
    #objects manager: devuelve todos los objetos con campo Alive=True
    objects = AliveFotoManager()
    #raw_objects manager: devuelve todos los objetos sin filtrar         
    raw_objects = models.Manager()
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default="E")
    #temporada_habilitado: indica si la foto esta habilitada para ser votada
    #                       en la temporada actual
    temporada_habilitado = models.CharField(max_length=1,
                                            choices=HABILITADO_CHOICES,
                                            default="S")
    height = models.IntegerField(null = True)
    width = models.IntegerField(null = True)    
    codigo_user = models.ForeignKey(User, related_name='fotos',
                                    verbose_name=u"Cliente", null=True)    
    categoria = models.ForeignKey(Categoria, verbose_name = u'Categoría',
                                  null=True)

    def highlyRandomName(self, filename, longitud=20):
        """
        retorna un nombre aleatorio de longitud igual a 'longitud',
        manteniendo la extension de la imagen
        """
        lista_letras_numeros = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        name="".join([random.choice(lista_letras_numeros) for i in xrange(longitud)])
        root, ext = os.path.splitext(filename)
        return name+ext

    def get_user_photo_path(self, filename):
        return u'%s%s/%s' % (settings.USERPHOTOS_FOLDER_PATH,
                             self.codigo_user.id, self.highlyRandomName(filename))
        #return u'%s%s/%s' % (settings.USERPHOTOS_FOLDER_PATH,
        #                     self.codigo_user.id, filename)
    
    #foto = models.ImageField('Foto', upload_to=get_user_photo_path,
    #                         width_field='width', height_field='height',
    #                         validators=[size_validator])
    foto = ImageWithThumbsField(
        'Foto',
        upload_to=get_user_photo_path,
        width_field='width', height_field='height',
        blank=True, null=True,
        storage=PUBLIC_MEDIA_BUCKET, thumbnail_format='jpeg',
        thumbs=(
        ('50x50', {'size': (50, 50), 'crop':'center', 'upscale':True}),
        ('65x65', {'size': (65, 65), 'crop':'center', 'upscale':True}),
        ('115x111', {'size': (115, 111), 'crop':'center', 'upscale':True}),
        ('122x116', {'size': (122, 116), 'crop':'center', 'upscale':True}),
        ('200x200_upscale', {'size': (200, 200), 'crop':False, 'upscale':True,}),
        ('220x220_upscale', {'size': (220, 220), 'crop':False, 'upscale':True,}),
        ('600x600_upscale', {'size': (600, 600), 'crop':False, 'upscale':True,}),
        ))    
    
    titulo = models.CharField(u'Título', max_length=50)
    descripcion = models.TextField(u'Descripcion', blank=True, null=True)
    ediciones = models.TextField(u'Ediciones', blank=True, null=True)
    #fans = models.ManyToManyField(User, blank=True, null=True)
    #vistas: nro de veces que fue vista la foto
    vistas = models.IntegerField(default=0)
    #num_favoritos: nro de votos que tiene la foto
    num_favoritos = models.IntegerField(default=0)
    ganadora_temporada = models.ForeignKey(Temporada, null=True, blank=True)
    fecha = models.DateTimeField(default=datetime.now)
    #alive: True si la foto esta activa
    #       False su la foto fue eliminada
    alive = models.BooleanField(default=True)
    #panoramica:True si es una foto panoramica
    #           False: si no lo es
    panoramica = models.BooleanField(default=False)
    rechazo = models.TextField(verbose_name=u"Razón del rechazo",
                               blank=True, null=True)
    #comment this function to allow uploading and voting on the same voting 
    #period
    #also review the funcion remaining_uploads and the template a-enter.html
    # def __init__(self, *args, **kwargs):
    #     """
    #         inicializa el objeto
    #         si actualmente se esta dentro de una temporada, se inhabilita la
    #         la foto para que no pueda ser votada en la temporada actual
    #         NOTA: si se quiere habilitar todas las fotos quitar este init
    #             y volver a poner en el admin la funcion habilitar fotos.
    #     """
    #     super(self.__class__, self).__init__(*args, **kwargs)
    #     temporada = Temporada()
    #     current_temporada = temporada.get_current_temporada()
    #     if current_temporada:
    #         if current_temporada.fecha_inicio <= self.fecha and \
    #                current_temporada.fecha_fin >= self.fecha:
    #             self.temporada_habilitado = "N"
    
    def __unicode__(self):
        return u'%s' % self.titulo

    def has_been_modified(self):
        """
        retorna una lista [boolean, boolean, boolean] indicando si el objeto
        fue modificado o no, el orden de los booleanos en esta lista indican
        [modificado, estado(modificado), panoramica(modificado)]
        si el objeto ya estaba registrado en la DB y
        ha sido modificado en sus atributos estado y/o panoramica
        retorna [True, ..] en los 2 atributos restantes indica cual o cuales de
        esos atributos fueron modificados
        retorna [False, False, False] si no ha sido modificado en sus atributos
        estado y/o panoramica  o si no esta registrado en la DB 
        """
        lista = [False, False, False]
        #if self.id and self.estado == True:
        if self.id:
            originalFoto = Foto.objects.get(id=int(self.id))
            if originalFoto.estado != self.estado:
                lista[0]=True
                lista[1]=True
            if originalFoto.panoramica != self.panoramica:
                lista[0]=True
                lista[2]=True
        return lista

    def requires_send_mail(self):
        """
        Retorna una lista [True, boolean, boolean] si
        el objeto no esta grabado en la DB o si lo esta y ha sido modificado en
        en sus atributos estado o panoramica. Los booleanos en la lista
        corresponden a [requiere_mail, estado, panoramico]
        en todos los demas casos retorna [False, False, False]
        """
        if not self.id:
            return [True, True, True]
        if self.has_been_modified()[0]:
            return self.has_been_modified()
        return [False, False, False]

    def increasePoints(self):
        """
        incrementa los puntos acumulados en el userprofile
        """
        self.codigo_user.get_profile().add_points(10)

    def save(self, *args, **kwargs):
        """
        Si la foto ha sido marcada como Rechazada se le debe envíar un mail al
        propietario con la razón por la que no fue aceptada y cambiar alive a
        False para que no sea mostrada
        tambien envía un mail de aceptacion de la foto
        tambien envia un mail si la foto fue marcada como panorámica
        solo envia el mail si el usuario esta habilitado para recibir correos
        """
        
        #hay q hacer un if pra ver si existia
        #hay que hcer un if pra ver si cambio de estado
        lista=self.requires_send_mail()
        if lista[0]:            
            if lista[1]:
                if self.estado == u"R":
                    self.alive = False
                    user = UserProfile.objects.get(user=self.codigo_user)
                    # Enviar el mail con la información de rechazo                    
                    data = {'user_firstname': self.codigo_user.first_name,
                            'photo_title': self.titulo,
                            'reason': self.rechazo,
                            'email':self.codigo_user.email,
                            'mydomain': Site.objects.get(id=1).domain,
                            'encryptedUsername': urlsafe_b64encode(str(self.codigo_user.id))}                            
                    if self.codigo_user.get_profile().idioma == u'es':
                        subject= u"Machu Picchu 100 – Tu foto no ha sido aceptada "
                        template = "a-photo-rejected_es.html"
                    else:
                        subject = u"Machu Picchu 100 – Your Photo was not accepted"
                        template = "a-photo-rejected_en.html"
                    if user.accept_email_updates:
                        sendHtmlMail("info@machu-picchu100.com", subject,
                                     template,
                                     data, self.codigo_user.email) 
                if self.estado == u"M":
                    self.increasePoints()
                    user = UserProfile.objects.get(user=self.codigo_user)
                    # Enviar el mail con la información de aceptación
                    data = {'user_firstname': self.codigo_user.first_name,
                            'photo_title': self.titulo,
                            'email': self.codigo_user.email,
                            'mydomain': Site.objects.get(id=1).domain,
                            'encryptedUsername': urlsafe_b64encode(str(self.codigo_user.id))}                            
                    if self.codigo_user.get_profile().idioma == u'es':
                        subject = u"Machu Picchu 100 - Tu Foto ha sido Aceptada"
                        template = 'a-photo-accepted_es.html'
                    else:
                        subject = u"Machu Picchu 100 - Your Photo has been Accepted"
                        template = 'a-photo-accepted_en.html'
                    #return "data_values %s, data_keys %s, idioma %s, accept_email_updates %s" % (data.values(), data.keys(), self.codigo_user.get_profile().idioma, user.accept_email_updates)
                    if user.accept_email_updates:
                        sendHtmlMail("info@machu-picchu100.com", subject,
                                     template,
                                     data, self.codigo_user.email)                      

            if lista[2]:
                if self.width >= self.height * 2 or self.panoramica:
                    self.panoramica = True
                    # user = UserProfile.objects.get(user=self.codigo_user)
                    # data = {'user_firstname': self.codigo_user.first_name,
                    #         'photo_title': self.titulo,
                    #         'email': self.codigo_user.email,
                    #         'mydomain': Site.objects.get(id=1).domain,
                    #         'encryptedUsername': urlsafe_b64encode(str(self.codigo_user.id))}
                    # if self.codigo_user.get_profile().idioma == u'es':
                    #     subject = u"Machu Picchu 100 - Tu foto panorámica puede ganar un Premio Especial Machu Picchu 100"
                    #     template = "a-photo-panoramic_es.html"
                    # else:
                    #     subject = u"Machu Picchu 100 - Your Panoramic Photo could win a Machu Picchu 100 Special Award!"
                    #     template = "a-photo-panoramic_en.html"
                    # if user.accept_email_updates:                    
                    #     sendHtmlMail("info@machu-picchu100.com", subject,
                    #                  template,
                    #                  data, self.codigo_user.email)

        return super(Foto, self).save(*args, **kwargs)

    
    @models.permalink
    def get_absolute_url(self):
        return ('portal_photo_vote', (), {'user_id': self.codigo_user.id,
                                          'foto_id': self.id, 'mis_fotos': 0 }) 
        #return ('fotos_navegar_foto', (), {'user': self.codigo_user.username,
        # 'foto_id': self.id, 'mis_fotos': 0 })

    #ToDo: como cambie esta funcion para que funcione con la temporada actual
    #si hay un error revisar esta funcion y la sgte, 
    def get_nro_votos(self):
        """
        Devuelve el nro de fans de una foto en el periodo de votacion actual
        """
        return self.fans().count()

    def get_nro_votos_on_temporada(self, temporada):
        """
        Devuelve el nro de fans de una foto en el periodo de votacion
        "temporada"
        en caso no exista 'temporada' retorna 0
        """
        temp = Temporada.objects.filter(id=int(temporada.id))
        if temp:
            return self.fans_on_temporada(temporada).count()
        return 0    
    
    def add_vista(self):
        """
        Aumenta en uno el número de visitas a una foto
        """
        self.vistas += 1
        self.save()
        
    def add_num_favoritos(self):
        """
        Aumenta en uno el número de votos de la foto
        """
        self.num_favoritos += 1
        self.save()
        
    
    def reset_num_favoritos(self):
        """
        Reinicia el contador de fotos a 0
        """
        self.num_favoritos = 0
        self.save()
        
    def enable(self):
        """
        Habilita la foto para el periodo de votacion
        """
        self.temporada_habilitado="S"
        self.save()
        
    def vista_previa(self):
        """
        Muestra una vista previa de la foto, se utilizará en el admin para 
        elegir las fotos por los jurados
        muestra el thumbnail y un link a la foto original
        """
        if self.foto:
#            thumbnail_options = dict(size=(200, 200), upscale=True, detail=True)
#            from sorl.thumbnail import get_thumbnail
#            thumbnail_img = get_thumbnail(self.foto.url, '200x200',crop='center',
#                                          quality=99)
#            return u'<a href="{0}/{1}"><img src="{0}/{1}" width="200" /></a>'.format(settings.S3_UPLOAD_URL, thumbnail_img.name)              
            return u'<a href="%s"><img src="%s" width="200" /></a>' % (self.foto.url, self.foto.generate_url('200x200_upscale'.strip()))
    
    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True
    
    def set_season_winner(self, season):
        """
        Esta foto es una ganadora de temporada
        """
        self.ganadora_temporada = season
        self.save()

    def allFans(self):
        """
        devuelve un lista de todos los usuarios que han votado por la foto
        sin filtrar por la temporada actual
        """
        return self.voto_set.all().values_list('codigo_user', flat=True)
        
    def fans_on_temporada(self, temporada):
        """
        devuelve un lista de todos los usuarios que han votado por la foto
        en la temporada 'temporada'
        en caso no exista la temporada devuelve []
        """
        votingTemporada = Temporada.objects.filter(id=int(temporada.id))
        return self.voto_set.filter(
            codigo_temporada__id=\
            votingTemporada[0].id).values_list('codigo_user', flat=True)

    #ToDo: como cambie de fans a solo los fans de la temporada actual
    #hay q revisar y hacer los reemplazos necesarios con all_fans o
    # fans_on_temporada donde se requiera
    def fans(self):
        """
        devuelve un lista de todos los usuarios que han votado por la foto
        en la temporada actual
        si no se esta en una temporada retorna []
        """
        currentVoingTemporada = Temporada().get_Current_Voting_Temporada()
        if currentVoingTemporada:
            return self.voto_set.filter(
                codigo_temporada=currentVoingTemporada).values_list(
                'codigo_user', flat=True)
        return self.voto_set.none()

    def get_user_language(self):
        """
        Retorna el idioma del dueño de la foto
        """
        # TODO: retornar el lenguaje
        return self.codigo_user
    get_user_language.short_description = 'User language'
    
    def deleteAllVotes(self):
        """
        Establece el estado alive = False, a todos los votos de la foto
        """
        for voto in self.voto_set.iterator():        
            voto.alive = False
            voto.save()

    def delete_foto(self):
        """
        Marca la foto como inactiva
        """
        self.alive = False
        super(Foto, self).save()

    def get_act_str(self):
        """
        Retorna el html de su activity stream 
        """
        _url = self.codigo_user.get_profile().get_absolute_url()
        if get_language() == 'en':
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">The user <a href="%s">%s</a> has uploaded a new photo: <a href="%s">"%s"</a>.</div></div>' % (_url,self.codigo_user.get_profile().foto.generate_url('50x50'.strip()),_url,self.codigo_user.username,self.get_absolute_url(),self.titulo)
        else:
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">El usuario <a href="%s">%s</a> subió una nueva foto: <a href="%s">"%s"</a>.</div></div>' % (_url,self.codigo_user.get_profile().foto.generate_url('50x50'.strip()),_url,self.codigo_user.username,self.get_absolute_url(),self.titulo)


    get_act_str.allow_tags=True


class GranGanador(models.Model):
    """
    ganadores elejidos por el jurado
    """
    codigo_foto = models.ForeignKey(Foto, 
                                    verbose_name='Ganadores Finales', 
                                    null=True)
    comentario = models.TextField()
    #winner indica que es un ganador que debe ser mostrado en la vista
    #de ganadores finalists/
    winner = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = u'Ganadores Finales'

    def __unicode__(self):
        return u'%s' % self.codigo_foto.titulo

    def vista_previa(self):
        """
        Muestra el thumbnail y un link a la foto original
        """
        if self.codigo_foto.foto:
            return u'<a href="%s"><img src="%s" width="200" /></a>' % (self.codigo_foto.foto.url, self.codigo_foto.foto.generate_url('200x200_upscale'.strip()))

    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True

    def titulo_foto(self):
        """
        Muestra el titulo de la foto
        """
        if self.codigo_foto:
            return u'%s' % self.codigo_foto.titulo

    titulo_foto.short_description = u'Título'
    titulo_foto.allow_tags = True

    def categoria_foto(self):
        """
        Muestra la categoría de la foto
        """
        return u'%s' % self.codigo_foto.categoria

    categoria_foto.short_description = u'Categoría'
    categoria_foto.allow_tags = True

class PanoramicWinner(models.Model):
    """
    ganadores entre la fotos panorámicas elegidas por Sony
    """
    codigo_foto = models.ForeignKey(Foto, 
                                    verbose_name='Ganadores Panorámicos', 
                                    null=True)
    comentario = models.TextField()
    winner = models.BooleanField(default=False)
    class Meta:
        verbose_name = u'Ganador Panorámico'
        verbose_name_plural = u'Ganadores Panorámicos'

    def __unicode__(self):
        return u'%s' % self.codigo_foto.titulo

    def vista_previa(self):
        """
        Muestra el thumbnail y un link a la foto original
        """
        if self.codigo_foto.foto:
            return u'<a href="%s"><img src="%s" width="200" /></a>' % (self.codigo_foto.foto.url, self.codigo_foto.foto.generate_url('200x200_upscale'.strip()))

    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True

    def titulo_foto(self):
        """
        Muestra el titulo de la foto
        """
        if self.codigo_foto:
            return u'%s' % self.codigo_foto.titulo

    titulo_foto.short_description = u'Título'
    titulo_foto.allow_tags = True

    def categoria_foto(self):
        """
        Muestra la categoría de la foto
        """
        return u'%s' % self.codigo_foto.categoria

    categoria_foto.short_description = u'Categoría'
    categoria_foto.allow_tags = True

class ProfessionalWinner(models.Model):
    """
    fotos profesionales seleccionadas
    """
    codigo_foto = models.ForeignKey(Foto, 
                                    verbose_name=u'Fotos Profesionales', 
                                    null=True)
    comentario = models.TextField()
    winner = models.BooleanField(default=False)
    class Meta:
        verbose_name = u'Ganador Profesional'
        verbose_name_plural = u'Ganadores Profesionales'

    def __unicode__(self):
        return u'%s' % self.codigo_foto.titulo

    def vista_previa(self):
        """
        Muestra el thumbnail y un link a la foto original
        """
        if self.codigo_foto.foto:
            return u'<a href="%s"><img src="%s" width="200" /></a>' % (self.codigo_foto.foto.url, self.codigo_foto.foto.generate_url('200x200_upscale'.strip()))

    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True

    def titulo_foto(self):
        """
        Muestra el titulo de la foto
        """
        if self.codigo_foto:
            return u'%s' % self.codigo_foto.titulo

    titulo_foto.short_description = u'Título'
    titulo_foto.allow_tags = True


class AliveVotoManager(models.Manager):
    """
    Devuelve todos los votos con estado alive
    """
    def get_query_set(self):
        return super(AliveVotoManager, self).get_query_set().filter(
            alive=True)

class Voto(models.Model):
    """
    Datos de un voto, guarda de que foto es, que usuario lo hizo
    y en que temporada se realizo
    """
    codigo_user = models.ForeignKey(User, blank=True, null=True)
    codigo_foto = models.ForeignKey(Foto, blank=True, null=True)
    codigo_temporada = models.ForeignKey(Temporada, blank=True, null=True)
    alive = models.BooleanField(default=True)

    #objects manager: devuelve todos los votos con alive=True
    objects = AliveVotoManager()
    #raw_objects manager: devuelve todas las denuncias sin filtrar
    raw_objects = models.Manager()

    def increasePoints(self):
        """
        incrementa la puntuacion del user profile tanto del usuario 
        votante como del usuario votado
        """
        self.codigo_user.get_profile().add_points(2)
        self.codigo_foto.codigo_user.get_profile().add_points(1)

    def get_act_str(self):
        """
        Retorna el html de su activity stream 
        """
        _url = self.codigo_user.get_profile().get_absolute_url()
        if get_language() == 'en':
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">The user <a href="%s">%s</a> has voted for your photo: <a href="%s">"%s"</a>.</div></div>' % (_url,self.codigo_user.get_profile().foto.generate_url('50x50'.strip()),_url,self.codigo_user.username,self.codigo_foto.get_absolute_url(),self.codigo_foto.titulo)
        else:
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">El usuario <a href="%s">%s</a> votó por tu foto: <a href="%s">"%s"</a>.</div></div>' % (_url,self.codigo_user.get_profile().foto.generate_url('50x50'.strip()),_url,self.codigo_user.username,self.codigo_foto.get_absolute_url(),self.codigo_foto.titulo)

    get_act_str.allow_tags=True


#class AliveDenunciaManager(models.Manager):
#    """
#    DEvuelve todas las denuncias con estado alive
#    """
#    def get_query_set(self):
#        return super(AliveDenunciaManager, self).get_query_set().filter(
#            respuesta=u"E")

class Denuncia(models.Model):
    """
    Guarda todos los datos de una denuncia reportada respecto a una foto:
    quien la hizo, sobre que foto fue, en que temporada se realizo
    la fecha, la razon y/o el comentario
    Los registros nunca se borran solo cambia su cambio alive a False
    """
    TIPO_RAZONES = ((u'1',"This image contains obscene or offensive content."),
                    (u'2',"This photo was not taken in or en route to the\
                           sanctuary of Machu Picchu"),
                    (u'3',"This photo was not taken by the user who submitted\
                           it or the user does not have rights to this photo."),
                    (u'4',"The image has been modified (for example, objects\
                           and/or people who were not present have been added)\
                           or edits not permitted were made (for example, \
                           drastic changes in the saturation and the exposure\
                           or use of digital filters)."),
                    (u'5',"This photo was miscategorized (for example, a\
                          photograph without a person was placed in the \
                          category 'People').")
                    )
    ##objects manager: devuelve todas las denuncias con alive=True
    #objects = AliveDenunciaManager()
    ##raw_objects manager: devuelve todas las denuncias sin filtrar
    #raw_objects = models.Manager()
    
    codigo_foto = models.ForeignKey(Foto)
    codigo_user = models.ForeignKey(User)
    codigo_temporada = models.ForeignKey(Temporada, blank=True, null=True)
    fecha = models.DateTimeField(default=datetime.now)
    razon = models.CharField(max_length=1, choices=TIPO_RAZONES)
    comentario  = models.TextField()
    RESPUESTA_CHOICES = (
        (u"A", u"Aceptada"),
        (u"R", u"Rechazada"),
        (u"E", u"Espera"),
    )
    respuesta = models.CharField(max_length=1, choices=RESPUESTA_CHOICES,
                                 default=u"E")

    def vista_previa(self):
        """
        Muestra una vista previa de la foto, se utilizará en el admin en la
        vista de denuncias,
        muestra el thumbnail y un link a la foto original 
        """
        if self.codigo_foto.foto:
            #thumbnail_options = dict(size=(200, 200), upscale=True, detail=True)
            ##thumbnail_img = get_thumbnailer(self.codigo_foto.foto).get_thumbnail(thumbnail_options)
            #from sorl.thumbnail import get_thumbnail
            #thumbnail_img = get_thumbnail(self.codigo_foto.foto.url, '200x200',
            #                              crop='center', quality=99)
            #return u'<a href="/media/%s"><img src="/media/%s" width="200" /></a>' % (self.codigo_foto.foto,thumbnail_img.name.replace('\\','/'))              
            return u'<a href="%s"><img src="%s" width="200" /></a>' % (self.codigo_foto.foto.url, self.codigo_foto.foto.generate_url('200x200_upscale'.strip()))
        
    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True

    def save(self, *args, **kwargs):
        """
        Pone la foto en estado alive=False sólo si ha sido aceptada
        la denuncia y no ha sido puesta en este estado anteriormente
        """
        if self.respuesta == u"A" and self.codigo_foto.alive:
            self.codigo_foto.alive = False
            #self.codigo_foto.save()
            super(Foto, self.codigo_foto).save(*args, **kwargs)
            self.codigo_foto.deleteAllVotes()
            #self.codigo_foto.save()
            super(Foto, self.codigo_foto).save(*args, **kwargs)

            current_temp=Temporada().get_current_temporada()
            past_temp=Temporada().get_last_temporada()
            if current_temp:
                if current_temp.is_in_this_temporada(datetime.now()):
                    if current_temp.is_in_this_temporada(self.codigo_foto.fecha):
                        self.codigo_user.get_profile().uploaded_photos-=1;
                        self.codigo_user.get_profile().save()                    
                else:
                    if not past_temp or past_temp.fecha_fin <= self.codigo_foto.fecha:
                        self.codigo_user.get_profile().uploaded_photos-=1;
                        self.codigo_user.get_profile().save()                    
        return super(Denuncia, self).save(*args, **kwargs)

class BadgeImage(models.Model):
    """
    guarda las imagenes, nombres y descripciones de los badges 
    """
    def highlyRandomName(self, filename, longitud=20):
        """
        retorna un nombre aleatorio de longitud igual a 'longitud',
        manteniendo la extension de la imagen
        """
        lista_letras_numeros = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        name="".join([random.choice(lista_letras_numeros) for i in xrange(longitud)])
        root, ext = os.path.splitext(filename)
        return name+ext

    def get_badge_path(self, filename):
        return u'%s/%s' % (settings.BADGES_FOLDER_PATH,
                             self.highlyRandomName(filename))
    height = models.IntegerField(null = True, blank=True)
    width = models.IntegerField(null = True, blank=True)
    foto = ImageWithThumbsField(
        'Foto',
        upload_to=get_badge_path,
        width_field='width', height_field='height',
        blank=True, null=True,
        storage=PUBLIC_MEDIA_BUCKET, thumbnail_format='jpeg',
        thumbs=(
        ('50x50', {'size': (50, 50), 'crop':'center', 'upscale':True}),
        ('75x75', {'size': (75, 75), 'crop':'center', 'upscale':True}),
        ('96x96', {'size': (96, 96), 'crop':'center', 'upscale':True}),
        ))
    name_en = models.CharField(_(u'Name (English)'),max_length=100)
    name_es = models.CharField(_(u'Name (Spanish)'),max_length=100)
    description_en = models.TextField(_(u'Description (English)'))
    description_es = models.TextField(_(u'Description (Spanish)'))

    def __unicode__(self):
        return u'%s' % self.name_en

    def vista_previa(self):
        """
        Muestra el thumbnail y un link a la foto original
        """
        if self.foto:
            return u'<a href="%s"><img src="%s" width="75" /></a>' % (self.foto.url, self.foto.generate_url('75x75'.strip()))
    
    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True



class UserProfile(models.Model):
    """
    Datos para un usuario sin privilegios
    IMPORTANTE: se habilito la funcion de devolver votos a los usuarios
    para revisar las fotos subidas es necesario quitar las que esten
    alive=False, tener en cuenta con los votos tambien
    
    """    
    FEMENINO_ = u'F'
    MASCULINO_ = u'M'
    
    tipo_sexo=( ( FEMENINO_, _(u'Female') ),
                ( MASCULINO_, _(u'Male') ),)
    
    tipo_titulo = ( 
        (u'Mr.', "Mr"),
        (u'Mrs.', "Mrs"),
        (u'Ms.', "Ms"),
        (u'Miss.',"Miss"),
        (u'Dr.',"Dr"),
    )
    
    #favoritos =  FavoritosUserProfileManager()
    objects = models.Manager()

    def get_user_photo_path(self, filename):
        return u'%s%s/%s' % (settings.USERPROFILE_PHOTO_PATH, self.id,
                             filename)          
    user = models.OneToOneField(User)
    height = models.IntegerField(null = True)
    width = models.IntegerField(null = True)
    foto = ImageWithThumbsField(
        'Foto',
        upload_to=get_user_photo_path,
        width_field='width', height_field='height',
        blank=True, null=True,
        storage=PUBLIC_MEDIA_BUCKET, thumbnail_format='jpeg',
        thumbs=(
        ('50x50', {'size': (50, 50), 'crop':'center', 'upscale':True}),
        ('60x60', {'size': (60, 60), 'crop':'center',}),
        ('75x75', {'size': (75, 75), 'crop':'center', 'upscale':True}),
        ('113x118', {'size': (113, 118), 'crop':'center', 'upscale':True}),
        ('122x116', {'size': (122, 116), 'crop':'center', 'upscale':True}),
        ('156x146', {'size': (156, 146), 'crop':'center', 'upscale':True}),
        ))
    fecha_nacimiento = models.DateField('fecha de nacimiento', 
                                        help_text='(dd-mm-aaaa)', null=True)
    sexo = models.CharField(max_length=1, choices=tipo_sexo)
    titulo = models.CharField(max_length=5, choices=tipo_titulo)
    pais = models.ForeignKey(Country, null=True)
    LANGUAGE_CHOICES = (
        (u"en", u"English"),
        (u"es", u"Spanish")
    )
    idioma = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,
                              default=u'es')
    #me_gusta_temp: nro de votos
    me_gusta_temp = models.IntegerField(default="0")
    #favoritos = models.ManyToManyField(Foto, blank=True, null=True)
    amigos = models.ManyToManyField('self', blank=True, null=True)
    accept_email_updates = models.BooleanField(
        'Aceptar actualizaciones por correo',
        blank=True, default=False)
    accept_sponsors_emails = models.BooleanField(
        'Aceptar correos de los auspiciadores',
        blank=True, default=False)
    #uploaded_photos: nro de fotos que subio el usuario
    uploaded_photos = models.IntegerField('Fotos subidas', null=True,
                                          blank=True, default=0)
    #points: puntos ganados como embajadores
    points = models.IntegerField('Puntos', default=0, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, null=True, blank=True)
    is_winner = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = u'Cliente'
    
    def __unicode__(self):
        return u'%s' % self.user.get_full_name()
    
    @models.permalink
    def get_absolute_url(self):
        return ('usuario_public_profile', (), { 'user_id': self.user.id })
        #return ('fotos_perfil_publico', (), { 'object_id': self.user.id })
        
    def set(self, foto, fecha_nacimiento, sexo, titulo, pais, idioma, departamento):
        if not foto:
            foto = self.foto    
        self.foto = foto
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo
        self.titulo = titulo
        self.pais = pais
        self.idioma = idioma
        if departamento:
            if (pais.printable_name == u'Peru'):            
                self.departamento = departamento
            else:
                self.departamento = None
        return self
    
    def clear_data(self):
        """Borra los datos"""
        self.height = ''
        self.width = ''
        self.foto = ''
        fecha_nacimiento = ''
        sexo = ''
        pais = ''
    
    def nuevo_voto(self):
        """
        Aumenta en uno el número de votos que hizo el usuario en una temporada
        """
        self.me_gusta_temp += 1
        self.save()
        
    def clear_season(self):
        """
        Reinicia el contador de votos en una temporada
        """
        self.me_gusta_temp = 0
        self.save()

    def remaining_votes(self):
        """
        Retorna el numero restante de votos
        """
        r = 5 - self.me_gusta_temp;
        return u'%i' % r
        
    def has_remaining_votes(self):
        """
        Retorna True si aun tiene votos disponibles
        en caso contrario retorna False
        """
        if (5 - int(self.me_gusta_temp)) > 0:
            return True
        return False
        
    def reset_uploaded_photos(self):
        """
        Reinica la variable uploaded_photos a 0
        """
        self.uploaded_photos = 0
        self.save()
        
    def remaining_uploads(self):
        """
        Retorna cuantas fotos aun puede subir el usuario
        siempre y cuando exista una temporada siguiente
        Si no existe, retorna 0
        """
        #para subir fotos en la misma temporada
        return 5 - self.uploaded_photos
        ####normal behavior
        # next_temporada = Temporada().get_next_temporada()
        # if next_temporada:
        #     r = next_temporada.max_fotos_per_user - self.uploaded_photos
        #     return r        
        # return 0        
    
    def increase_uploaded_photos(self):
        """
        Incremente el nro de fotos subidas por el usuarios
        """
        self.uploaded_photos +=1;
        self.save()
        return ''

    def favoritos(self):
        """
        Retorna todas las fotos por las que voto el usuario
        Es lo mismo que hacia la FK favoritos del modelo anterior
        """
        return  Foto.objects.filter(voto__codigo_user__id = self.user.id)
        
    def get_total_votes_of_my_votes_in_this_temporada(self, temporada_id):
        """
        SOLO FUNCIONA ANTES QUE SE REINICIEN LAS VARIABLES num_favoritos
        FUE CREADA PARA USO EXCLUSIVO DEL CRONJOB DE FIN DE TEMPORADA
        retorna el total de votos que obtuvieron las fotos por las que voto
        el usuario, en la temporada con id = temporada_id
        """
        my_votes = self.user.voto_set.filter(codigo_temporada__id=temporada_id)
        total = 0
        for vote in my_votes:
            total += int(vote.codigo_foto.num_favoritos)
        return total
    
    def get_votes_from_this_temporada(self, temporada):
        """
        retorna todos los votos realizados por el usuario en la temporada
        'temporada_id'
        """
        return self.user.voto_set.filter(codigo_temporada=temporada)

    def get_photos_voted_from_this_temporada(self, temporada):
        """
        retorna una lista las fotos por las que voto el usuario en la temporada
        'temporada'
        """
        votes = self.get_votes_from_this_temporada(temporada)
        return [f.codigo_foto for f in votes]
        
    def delete_user(self):
        """
        marca como inactivas todas sus fotos(y los votos de cada foto)
        y votos ademas inactiva su cuenta de usuario
        """
        for foto in self.user.fotos.all():
            foto.deleteAllVotes()
            foto.delete_foto()
            a=self.user
            a.is_active = False
            a.save()
    
    def set_as_winner(self):
        """
        marca al usuario como ganador
        """
        self.is_winner = True
        self.save()

    def add_points(self, i):
        """
        aniande 'i' puntos a self.points
        y evalua si le corresponde subir de nivel
        """
        self.points += i
        self.save()
        badges.possibly_award_badge("points_awarded", user=self.user)

    def get_level(self):
        """
        retorna el nivel al que pertenece el usuario
        """
        l=int(ceil(float(self.points)/1000))
        if l > 10:
            l = 10
        elif l == 0:
            l = 1
        return l

    def get_BadgeImage(self, level=''):
        """
        retorna el objeto BadgeImage correspondiente al nivel en que esta 
        el usuario
        si no hay ningun objeto BadgeImage creado retorna ''
        """
        if not level:
            level=self.get_level()
        try:
            bi = get_object_or_404(BadgeImage,id=level)
        except:
            bi = ''
        return bi

    def get_BadgeName_en(self):
        """
        retorna el nombre en ingles del badge actual del usuario
        """
        try:
            return u'%s' % self.get_BadgeImage().name_en
        except:
            return u''

    def get_BadgeName_es(self):
        """
        retorna el nombre en espaniol del badge actual del usuario
        """
        try:
            return u'%s' % self.get_BadgeImage().name_es
        except:
            return u''

    def get_act_str(self):
        """
        Retorna el html de su activity stream 
        """
        _url = self.get_absolute_url()
        if get_language() == 'en':
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">The user <a href="%s">%s</a> has reached the level "%s".</div></div>' % (_url,self.foto.generate_url('50x50'.strip()),_url,self.user.username,self.get_BadgeName_es())
        else:
            return u'<div class="span-13"><div class="span-2 last"><a href="%s"><img src="%s" width="50px" height="50px" /></a></div><div class="span-11 last">El usuario <a href="%s">%s</a> ha alcanzado el nivel "%s".</div></div>' % (_url,self.foto.generate_url('50x50'.strip()),_url,self.user.username,self.get_BadgeName_es())

    get_act_str.allow_tags=True


class ComentarioPerfil(models.Model):
    """
    Clase para los comentarios que se dejan en el perfil, sólo por usuarios 
    registrados
    """
    cliente = models.ForeignKey(UserProfile, related_name=u"cliente")
    amigo = models.ForeignKey(UserProfile, related_name=u"amigo")
    fecha = models.DateTimeField(default=datetime.now)
    texto = models.TextField()
    
    def __unicode__(self):
        return u"De %s para %s" % (self.amigo, self.cliente)
    
    class Meta:
        verbose_name = u"Comentario del perfil"
        verbose_name_plural = u"Comentarios del perfil"

    
class Solicitud_de_Amistad(models.Model):
    codigo_user = models.ForeignKey(User, related_name='solicitudes', null=True)
    codigo_user_solicitante = models.ForeignKey(User, related_name='+',
                                                null=True)
    #codigo_user_solicitante = models.ForeignKey(User,
    #related_name='solicitante')
    
    def __unicode__(self):
        return u'%s' % self.codigo_user_solicitante.first_name    

class Comentario(models.Model):
    """
    Modelo con los datos sobre un comentario
    """
    foto = models.ForeignKey(Foto)
    user = models.ForeignKey(User)
    fecha = models.DateField(default=datetime.now)
    texto = models.TextField()
    ESTADO_CHOICES = (
        (u"M", u"Moderado"),
        (u"E", u"Espera"),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default="E")

    def __unicode__(self):
        return u"%s, comentado por %s" % (self.foto, self.user.username)    
    
class Noticia(models.Model):
    #codigo_user = models.ForeignKey(User, related_name='noticias')
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=datetime.now)
    
    def __unicode__(self):
        return u'%s' % self.titulo

    @models.permalink
    def get_absolute_url(self):
        return ('fotos_ver_noticia', (), { 'object_id': self.id })


class Estadistica(models.Model):
    nro_fotos_subidas = models.IntegerField(u'Número de fotos subidas')
    nro_total_votos = models.IntegerField(u'Número total de votos emitidos')

    def __init__(self, *args, **kwargs):
        """
            inicializa el objeto
        """
        super(self.__class__, self).__init__(*args, **kwargs)
        self.nro_fotos_subidas = Foto.objects.all().count()
        self.nro_total_votos = Voto.objects.all().count()
    
    def __unicode__(self):
        return u'Estadísticas'
    
    def add_voto(self):
        """
        incrementa en 1 en campo nro_total_votos
        """
        self.nro_total_votos+=1
        self.save()
        
    def add_foto(self):
        """
        incrementa en 1 el campo nro_fotos_subidas
        """
        self.nro_fotos_subidas+=1
        self.save()

class TopAmbassador(models.Model):
    """
    guarda a los 10 usuarios más activos de cada semana
    """
    codigo_user = models.ForeignKey(User)    
    fecha = models.DateTimeField()
    points = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s' % self.codigo_user
    
    def get_last_top_10(self):
        """
        retorna una lista de los últimos 10 ganadores
        """
        try:
            queryset = TopAmbassador.objects.order_by("-id")
            last_date = queryset[0].fecha
            return queryset.filter(fecha=last_date)
        except:
            return []
            

def weekly_top_ambassadors():
    """
    calcula a los 10 embajadores mas activos de la semana
    """
    if User.objects.count() != 0:
        top10 = UserProfile.objects.order_by("-points")[:10]
        fecha=datetime.now()
        for u in top10:
            TopAmbassador.objects.create(codigo_user=u.user,
                                         fecha=fecha,
                                         points=u.points)
    return u'10 embajadores mas activos calculados'

def close_temporada():
    """
    Calcula los 10 ganadores mas votados (o mas si hay empates), permitiendo
    que cada usuario solo pueda ganar una vez y con una foto
    Calcula al ganador o ganadores por votos[DESACTIVADO]
    Reinicia el contador de votos en cada foto, excepto para las ganadoras
    Habilita todas las fotos que no estan habilitadas
    Reinicia el contador de votos de los usuarios
    """
    
    finished_temporada=Temporada().get_last_temporada()

    if finished_temporada:
        fotos = Foto.objects.filter(temporada_habilitado='S').filter(
            estado='M').exclude(
            ganadora_temporada__isnull=False).order_by("-num_favoritos")
        lista_fotos = []
        for foto in fotos:
            #evitanto que entren fotos de usuarios que ya son ganadores
            if not foto.codigo_user.get_profile().is_winner:
                lista_fotos.append(foto)            
        if lista_fotos:
            #obteniendo los 10 mas votados
            i=0
            position=0
            list_length = len(lista_fotos)
            winners=[]
            while i<10 and position<list_length:
                #p=lista_fotos[position].codigo_user.get_profile()
                p=UserProfile.objects.get(
                    id=lista_fotos[position].codigo_user.get_profile().id)
                if not p.is_winner:
                    winners.append(lista_fotos[position])
                    p.set_as_winner()
                    i+=1
                position+=1
                
            #obteniendo ganadores empates en el 10 lugar
            winners_length = len(winners)
            position = lista_fotos.index( winners[winners_length-1] ) + 1
            while position<list_length:
                if lista_fotos[position].num_favoritos == winners[winners_length-1].num_favoritos:
                    #p=lista_fotos[position].codigo_user.get_profile()
                    p = UserProfile.objects.get(
                        id=lista_fotos[position].codigo_user.get_profile().id)
                    if not p.is_winner:
                        winners.append(lista_fotos[position])
                        p.set_as_winner()
                    position+=1
                else:
                    break;            
            ## obtener la 10ma cantidad de votos (sin considerar duplicados)
            ## REVISAR SI DEVUELVE LOS 10 MAS VOTADOS
            #try:
            #    tenth_winer = fotos[10].num_favoritos
            #except:
            #    tenth_winer = fotos[fotos.count()-1].num_favoritos
            #winners_threshold = tenth_winer
            ## get all winners
            #winners = fotos.filter(num_favoritos__gte=winners_threshold)
            for w in winners:
                finished_temporada.foto_set.add(w)

        # #ganadores por votos(por sorteo) con una posibilidad de ganar por cada
        # # voto
        # winner_votos = []
        # all_votos = Voto.objects.filter(codigo_temporada=finished_temporada)
        # while len(winner_votos) < 10:
        #     if not all_votos:
        #         break
        #     winner = all_votos.order_by('?')[0].codigo_user
        #     winner_votos.append(winner)
        #     all_votos = all_votos.exclude(codigo_user=winner)
            
        # for w in winner_votos:
        #     # esto esta mal, hay que utilizar un count para esto
        #     #reply: ya que el nro de votos es irrelevante por ser ganadores
        #     #por sorteo, podemos obviar el campo num_votos, ya que ese campo
        #     #era para la manera antigua de calcular votos
        #     #num_votes = Voto.objects.filter(codigo_user=w,
        #     #                                codigo_temporada=finished_temporada,
        #     #                                ).count()
        #     #estoy retirando de su modelo el campo num_votos
        #     m = Ganador_Votos.objects.create(temporada=finished_temporada,
        #                                      user=w)
        
    # #num_favoritos=0, excepto para ganadores
        fotos_to_reset = Foto.objects.filter(temporada_habilitado='S'
                           ).exclude(ganadora_temporada__isnull=False)
        for foto in fotos_to_reset:
            foto.reset_num_favoritos()
    
    #habilitar todas las fotos que no estan habilitadas
        fotos_not_enabled = Foto.objects.filter(temporada_habilitado="N")
        for foto in fotos_not_enabled:
            foto.enable()
    
    #reinicia el contador de votos de los usuarios
        contestants = finished_temporada.get_contestants()
        if contestants:
            for contestant in contestants:
                contestant.get_profile().clear_season()

    return "Voting Period Closed"


def start_temporada():
    """
    Pone todos uploaded_photos a 0, para que puendan subir 5 fotos a la
    sgte temporada, haya o no. 
    """
    from MP100.fotos.models import UserProfile

    list_userprofile = UserProfile.objects.filter(uploaded_photos__gt=0)
    list_userprofile.update(uploaded_photos=0)
    return "Voting Period Started"

def inactivate_users(list_users):
    """
    Borra una lista de usuarios poniendo sus cuentas como inactivas,
    al igual que sus fotos y votos
    recibe una lista con los id's de los usuarios
    """
    for user_id in list_users:
        User.objects.get(id=user_id).get_profile().delete_user()

def recalculate_photoWinners(temporada):
    """
    Recalcula los ganadores de la temporada 'temporada'
    excluye a las fotos y votos que estan con estado alive = False
    """
    lista_fotos=[]
    #borrando los ganadores actuales
    for f in temporada.foto_set.all():
        f.ganadora_temporada = None
        super(Foto,f).save()
    #obteniendo un listado de tuplas de la forma (foto.id, num_votos)
    for foto in Foto.objects.filter(fecha__lt=temporada.fecha_inicio).filter(ganadora_temporada__isnull=True):
        #evitanto que entren fotos de usuarios que ya son ganadores
        if not foto.codigo_user.get_profile().is_winner:
            lista_fotos.append((foto.id,foto.voto_set.filter(codigo_temporada=temporada).filter(alive=True).count()))
    #ordenando de menor a mayor segun el numero de votos
    lista_fotos.sort(key = lambda num_votos: num_votos[1])
    #ordenadno de mayor a menor
    lista_fotos.reverse()
    #obteniendo los 10 mas votados
    #winners = lista_fotos[:10]
    i=0
    position=0
    list_length = len(lista_fotos)
    winners=[]
    while i<10 and position<list_length:
        p=Foto.objects.get(id=int(lista_fotos[position][0])).codigo_user.get_profile()
        if not p.is_winner:
            winners.append(lista_fotos[position])
            p.set_as_winner()
            i+=1
        position+=1
        
    #obteniendo ganadores empates en el 10 lugar
    winners_length = len(winners)
    position = lista_fotos.index( winners[winners_length-1] ) + 1
    while position<list_length:
        if lista_fotos[position][1] == winners[winners_length-1][1]:
            #winners.append(lista_fotos[position])
            #f=Foto.objects.get(id=int(lista_fotos[position][0]))
            #f.codigo_user.get_profile().set_as_winner()
            p=Foto.objects.get(id=int(lista_fotos[position][0])).codigo_user.get_profile()
            if not p.is_winner:
                winners.append(lista_fotos[position])
                p.set_as_winner()
            position+=1
        else:
            break;
                
    #asignando los nuevos ganadores
    for f in winners:
        foto = Foto.objects.get(id=f[0])
        foto.num_favoritos = f[1]
        super(Foto,foto).save()
        temporada.foto_set.add(foto)

def update_votingWinners(temporada):
    """
    actualiza los ganadores por sorteo de la temporada 'temporada',
    no vuelve a sortear, sólo quita a los ganadores con estado alive=False
    """
    for w in temporada.ganador_votos_set.all():
        if not w.user.is_active:
            w.delete()

def recalculate_temporadas(lista_temporadas, users_to_inactivate):
    """
    inactiva los votos, fotos y cuentas de los usuarios en la lista
    'users_to_inactivate'
    recalcula fotos ganadoras de la temporadas en la lista 'lista_temporadas'
    y quita a los usuarios ganadores (por sorteo) con
    estado alive = False (inactivos)
    IMPORTANTE: todas las temporadas a recalcular deben ser temporadas pasadas
    """
    inactivate_users(users_to_inactivate)
    for temporada in lista_temporadas:
        recalculate_photoWinners(temporada)
        update_votingWinners(temporada)

def script_recalcular_temp_1_a_temp_4():
    import csv
    spamReader = csv.reader(open('id_users_to_inactivate.csv', 'rb'))
    recalculate_temporadas(Temporada.objects.order_by("id")[:4],
                           [row[0] for row in spamReader])

def script_recalcular_actual_temp_5():
    """
    recalcula los votos de las fotos, teniendo en cuenta solo los votos activos
    osea con estado alive = True
    """
    for f in Foto.objects.exclude(ganadora_temporada__isnull=False).iterator():
        f.num_favoritos = f.voto_set.filter(codigo_temporada__id=5).filter(alive=True).count()
        f.save()

def script_recalcular_temp_1_5():
    script_recalcular_temp_1_a_temp_4()
    script_recalcular_actual_temp_5()
        
class kuna_photos(models.Model):
    """
    Guarda la seleccion de fotos para los premios regalados por Kuna
    """
    foto = models.ForeignKey(Foto, null=True, blank=True)
    fecha = models.DateTimeField(default=datetime.now)
    
    def __unicode__(self):
        return u'%s' % foto.titulo

    
class PointsBadge(Badge):
    slug = "points"
    levels = ['Pinas',
              'Yanas',
              'Mitmaqkuna',
              'Hatun Runa',
              _(u'Nobleza de Privilego'),
              _(u'Nobleza de Sangre'),
              'Auqui',
              'Coya',
              'Inca',
              'Inti',]
    events = [
        "points_awarded",
        ]

    multiple = False

    def award(self, **state):
       user = state["user"]
       level = user.get_profile().get_level()
       return BadgeAwarded(level=level)

        # if point >= 10000:
        #     return BadgeAwarded(level=10)
        # elif points >= 8000:
        #     return BadgeAwarded(level=9)
        # elif points >= 7000:
        #     return BadgeAwarded(level=8)
        # elif points >= 6000:
        #     return BadgeAwarded(level=7)
        # elif points >= 5000:
        #     return BadgeAwarded(level=6)
        # elif points >= 4000:
        #     return BadgeAwarded(level=5)
        # elif points >= 3000:
        #     return BadgeAwarded(level=4)
        # elif points >= 2000:
        #     return BadgeAwarded(level=3)
        # elif points >= 1000:
        #     return BadgeAwarded(level=2)
        # else:
        #     return BadgeAwarded(level=1)

badges.register(PointsBadge)




        
        

