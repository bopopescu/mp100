#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from MP100.fotos.models import UserProfile
from django.utils import translation


class Command(BaseCommand):
    """
    Pone todos uploaded_photos a 0, para que puendan subir 5 fotos a la
    sgte temporada, haya o no. 
    """
    help = 'Acciones realizadas para el inicio de una temporada'

    def handle(self, *args, **options):        
        # TODO: No sé si será necesario pero la documentación lo pide
        translation.activate('es-pe')
        
        list_userprofile = UserProfile.objects.filter(uploaded_photos__gt=0)
        for userprofile in list_userprofile:
            userprofile.reset_uploaded_photos()
        
        translation.deactivate()
        
