# -*- coding: utf-8 -*-

from django.db import models
from MP100.countries.models import Country


#hay q cambiar el nombre  a Red_Social
class Redes_Sociales(models.Model):
    nombre = models.CharField(max_length = 50)
    url = models.URLField(verify_exists = True)

    class Meta:
        verbose_name_plural = "Redes_Sociales"
    
    def __unicode__(self):
        return u'%s' % self.nombre

#class Lenguaje(models.Model):
#    nombre = models.CharField(max_length = 50)
#        
#    def __unicode__(self):
#        return u'%s' % self.nombre

    
#class Informacion(models.Model):
#    nombre = models.CharField(max_length = 50)
#    descripcion = models.TextField(max_length=1000)
#    
#    class Meta:
#        verbose_name_plural = "Informacion"
#    
#    def __unicode__(self):
#        return u'%s' % self.nombre 


class Banner(models.Model):
    """
    Banners administrados por país, tiempo y número de vistas
    """    
    ALIGN_CHOICES = (
        (u'H', u'Horizontal'),
        (u'V', u'Vertical'),
    )
    title = models.CharField(max_length=60, verbose_name=u"Nombre")
    align = models.CharField(max_length=1, choices=ALIGN_CHOICES, default=u'H',
                             verbose_name=u"Alineación")
    image = models.ImageField(upload_to="images/banners",
                              verbose_name=u"Imagen")
    country = models.ForeignKey(Country, verbose_name=u"Pais")
    clicks = models.IntegerField(default=0)
    timer = models.FloatField(verbose_name=u"Tiempo contratado")
    link = models.URLField(verbose_name=u"URL de enlace", verify_exists=False)
    
    def __unicode__(self):
        return "%s" % self.title
        
    def add_click(self):
        """
        Añade un click al banner
        """
        self.clicks += 1
        self.save()        
    
    def vista_previa(self):
        """
        Muestra una vista previa de la imágen del banner
        """
        if self.image:
            if self.align == u"H":
                return u'<img src="/media/%s" heigth="200" />' % self.image
            else:
                return u'<img src="/media/%s" width="200" />' % self.image
                
    vista_previa.short_description = u"Vista previa"
    vista_previa.allow_tags = True
    
