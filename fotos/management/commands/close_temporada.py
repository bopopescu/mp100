#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from MP100.fotos.models import Temporada, UserProfile, Foto, Categoria
from django.utils import translation


class Command(BaseCommand):
    """
    Calcula los 10 ganadores mas votados (o mas si hay empates)
    Calcula al ganador o ganadores por votos
    Reinicia el contador de votos en cada foto, excepto para las ganadoras
    Habilita todas las fotos que no estan habilitadas
    Reinicia el contador de votos de los usuarios
    """
    help = 'Cerra una temporda de votacion'

    def handle(self, *args, **options):        
        # TODO: No sé si será necesario pero la documentación lo pide
        translation.activate('es-pe')

        finished_temporada=Temporada().get_last_temporada()
        if finished_temporada:
        #10 ganadores mas votados (o mas si hay empate en 10mo lugar)
            fotos = Foto.objects.filter(temporada_habilitado='S').exclude(ganadora_temporada__isnull=False).order_by("-num_favoritos")
            if fotos:
                winners=fotos[:10]
                #verificando empates
                #si hay empate en 10 lugar, todos los que tengan por lo menos ese puntaje pasan
                nro=-1
                for winner in winners:
                    nro+=1
                if fotos.filter(num_favoritos=winners[nro].num_favoritos).count() > 1:
                    winners=fotos.filter(num_favoritos__gte=winners[nro].num_favoritos)
                for winner in winners:
                    finished_temporada.foto_set.add(winner)
                    
        #ganador o ganadores por votos
            contestants = finished_temporada.get_contestants()
            vote_winners=[]
            if contestants:
                max_votes=0
                for contestant in contestants:
                    tmp = contestant.get_profile().get_total_votes_of_my_votes_in_this_temporada(finished_temporada.id)
                    if tmp == max_votes:
                        vote_winners.append(contestant)		    
                    if tmp > max_votes:
                        vote_winners=[]
                        vote_winners.append(contestant)
                        max_votes = tmp
                if max_votes != 0:
                    for vote_winner in vote_winners:
                        m = Ganador_Votos.objects.create(temporada=finished_temporada,
                                          user=vote_winner,
                                          num_votos=max_votes)
        #num_favoritos=0, excepto para ganadores
            fotos_to_reset = Foto.objects.filter(temporada_habilitado='S').exclude(ganadora_temporada__isnull=False)
            for foto in fotos_to_reset:
                foto.reset_num_favoritos()
        
        #habilitar todas las fotos que no estan habilitadas
            fotos_not_enabled = Foto.objects.filter(temporada_habilitado="N")
            for foto in fotos_not_enabled:
                foto.enable()
        
        #reinicia el contador de votos de los usuarios
            if contestants:
                for contestant in contestants:
                    contestant.get_profile().clear_season()
                    
        translation.deactivate()
        
