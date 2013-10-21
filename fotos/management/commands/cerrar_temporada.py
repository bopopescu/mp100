#-*- coding: utf-8 -*-

#from django.core.management.base import BaseCommand, CommandError
#from MP100.fotos.models import Temporada, UserProfile, Foto, Categoria
#from django.utils import translation
#
#
#class Command(BaseCommand):
#    help = 'Acciones realizadas para el cierre de temporada'
#
#    def handle(self, *args, **options):        
#        # TODO: No sé si será necesario pero la documentación lo pide
#        translation.activate('es-pe')
#        
#        temporadas = Temporada.objects.all()
#        for temporada in temporadas:
#            if temporada.is_close_yesterday():
#                # Determinará los ganadores de la temporada, 10 ganadoras
#                # TODO: Desnormalizar para optmizar
#                fotos = Foto.objects.filter(categoria=categoria).order_by("-fans")
#                favoritas = []
#                for foto in fotos:
#                    repetida = False
#                    for favorita in favoritas:
#                        if favorita['foto'].id == foto.id:
#                            repetida = True
#                    if not repetida:
#                        favoritas.append(foto)
#                    fotos.fans.clear()
#                        
#                for favorita in favoritas[:10]:
#                    favorita.set_season_winner(temporada)
#                
#                # Colocar los contadores de votos de los usuarios en 0
#                # TODO: Desnormalizar el número de fans de la foto y resetear el contador también
#                users = UserProfile.objects.all()
#                for user in users:
#                    user.clear_season()
#                    
#        translation.deactivate()
#        
