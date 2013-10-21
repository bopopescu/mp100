from django.db import models

class Departamento(models.Model):
    nombre = models.CharField(max_length=128)

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        ordering = ['nombre',]
