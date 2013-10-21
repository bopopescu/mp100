from django.db.models.signals import post_save, pre_save
#import models #tiene el models correcto
import MP100.fotos.models
#from MP100.fotos.models import Categoria   
from django.contrib.auth.models import User
from django.conf import settings
import os

def create_profile(sender, instance, created, **kwargs):
    """ sender: modelo de la clase
        instance: instancia siendo grabada
        created: Booleano, true si un nuevo registro fue grabado
        using: el aleas de la DB"""
        
    user = instance
    if created:
        try:
            profile, created =\
                MP100.fotos.models.UserProfile.objects.get_or_create(
                user=user)
            profile.foto=settings.USERPROFILE_PHOTO_PATH+"no_image.jpg"
            profile.width = 113
            profile.height = 118
            profile.save()
        except:
            pass
post_save.connect(create_profile, sender=User)
    
