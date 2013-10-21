from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from MP100.countries.models import Country
from datetime import date
import signals


# Create your models here.
class UserProfile(models.Model):   
    FEMENINO_ = 1
    MASCULINO_ = 2
    
    tipo_sexo=((FEMENINO_,'Femenino'),
                (MASCULINO_,'Masculino'),)

    def get_user_photo_path(self, filename):
        return u'%s%s/%s' % (settings.USERPROFILE_PHOTO_PATH, self.id, filename)            
    
    user = models.ForeignKey(User, unique=True)
    height = models.IntegerField(null = True)
    width = models.IntegerField(null = True)
    #foto = models.ImageField('Foto', upload_to=settings.USERPROFILE_PHOTO_PATH, width_field='width',height_field='height')
    foto = models.ImageField('Foto', upload_to=get_user_photo_path, width_field='width',height_field='height', blank=True, null=True)
    fecha_nacimiento = models.DateField('fecha de nacimiento', help_text='(dd-mm-aaaa)', null=True)
    sexo = models.IntegerField("Sexo", max_length=1, choices=tipo_sexo, default=MASCULINO_) 
    pais = models.ForeignKey(Country, null=True)
    
    def __unicode__(self):
        return u'%s' % self.id
    
    def set(self, foto, fecha_nacimiento, sexo, pais):
        if not foto:
            foto = self.foto    
        self.foto = foto
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo
        self.pais = pais
        return self
    
    def clear_data(self):
        """Borra los datos"""
        self.height = ''
        self.width = ''
        self.foto = ''
        fecha_nacimiento = ''
        sexo = ''
        pais = ''

        
class Amigo(models.Model):
    codigo_user = models.ForeignKey(User, related_name='amigos')
    codigo_user_amigo = models.ForeignKey(User, related_name='mi_amigo')#derre aqui se deba poner 
    
    def __unicode__(self):
        return u'%s' % self.codigo_user_amigo.first_name
    
class Solicitud_de_Amistad(models.Model):
    codigo_user = models.ForeignKey(User, related_name='solicitudes')
    codigo_user_solicitante = models.ForeignKey(User, related_name='solicitante')
    
    def __unicode__(self):
        return u'%s' % self.codigo_user_solicitante.first_name
    
class Foto(models.Model):
    foto = models.ImageField('Foto', upload_to=settings.PHOTOS_PHOTO_PATH, width_field=100,height_field=200)
    titulo = models.CharField("T&iacute;tulo", max_length=50)
    descripcion = models.TextField('Descripcion', blank=True, null=True)
    me_gusta = models.IntegerField('Me gusta', max_length=10)
    codigo_user = models.ForeignKey(User, related_name='fotos')
    
    def __unicode__(self):
        return u'%s' % self.titulo
    
class Favorito(models.Model):
    codigo_user = models.ForeignKey(User, related_name='favoritos')
    codigo_foto = models.ForeignKey(Foto, related_name='favorito_por')
    
    def __unicode__(self):
        return u'%s' % self.codigo_foto
    
class Elegida(models.Model):
    codigo_foto = models.ForeignKey(Foto, related_name='elegida')
    
    def __unicode__(self):
        return u'%s' % self.codigo_foto
    
class Noticia(models.Model):
    codigo_user = models.ForeignKey(User, related_name='noticias')
    notitifacion = models.TextField()
    
    def __unicode__(self):
        return u'%s' % self.notitifacion

class Estadistica(models.Model):
    nro_usuarios = models.IntegerField('N&uacute;mero de usuarios')
    nro_fotos_subidas = models.IntegerField('N&uacute;mero de fotos subidas')
    total_visitas = models.IntegerField('Total de visitas')
    promedio_diario_visitas = models.IntegerField('Promedio diario de visitas')
    
    def __unicode__(self):
        return u'Estad&iacute;sticas'

    