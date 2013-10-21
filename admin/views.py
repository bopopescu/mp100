# -*- coding: utf-8 -*-

from django.core.mail.message import EmailMessage
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as __
from django.shortcuts import get_object_or_404, redirect
from MP100.common.utils import direct_response
#from backupdb import Command
from django.views.decorators.csrf import csrf_exempt
# models
from MP100.fotos.models import Foto, UserProfile, Comentario, Temporada, Country
# forms
from MP100.admin.forms import FavoritaForm, HabilitarFotosForm, SendEmailForm, VerifyVotosForm, DesqualifyUserForm
from django.contrib.admin.views.decorators import staff_member_required
import re

@staff_member_required
def show_fotos_for_kuna(request):
    """
    muestra las fotos moderadas del concurso para que puedan ser seleccionadas
    como ganadoras para kuna
    """
    return direct_response(request, "admin/kuna_photos/change_list.html",
                           {"fotos_list": Foto.objects.all(),})

@staff_member_required
def verify_votes(request):
    """
    muestra las fotos, no ganadoras, ordenadas en forma
    descendente según su número de votos,
    las fotos son links a una pagina para verificar sus votos

    """
    return direct_response(request, "admin/verify_votes/change_list.html",
                           {"fotos_list": Foto.objects.filter(
                            temporada_habilitado='S').filter(
                            estado='M').exclude(
                            ganadora_temporada__isnull=False).order_by(
                            "-num_favoritos"),})    

@staff_member_required
def show_all_votes(request, foto_id, pais_id):
    """
    muestra una página con todos los datos de los usuarios que votaron por la foto 
    con id = "foto_id" en la temporada actual de votación
    """
    foto=get_object_or_404(Foto, pk=int(foto_id))
    temporada=Temporada().get_Current_Voting_Temporada()
    profiles = []
    if temporada:
        for v in foto.voto_set.filter(codigo_temporada=temporada).filter(alive=True):
            if not pais_id and not request.POST:
                profiles.append((v.codigo_user.username, v.codigo_user.email,
                                 v.codigo_user.first_name, v.codigo_user.last_name,
                                 v.codigo_user.get_profile().fecha_nacimiento,
                                 v.codigo_user.get_profile().sexo,
                                 v.codigo_user.get_profile().pais,
                                 v.codigo_user.get_profile().departamento,
                                 v.codigo_user.get_profile().uploaded_photos,))
            else:
                if pais_id and not request.POST:
                    if int(v.codigo_user.get_profile().pais.numcode) == int(pais_id):
                        profiles.append((v.codigo_user.username, v.codigo_user.email,
                                         v.codigo_user.first_name, v.codigo_user.last_name,
                                         v.codigo_user.get_profile().fecha_nacimiento,
                                         v.codigo_user.get_profile().sexo,
                                         v.codigo_user.get_profile().pais,
                                         v.codigo_user.get_profile().departamento,
                                         v.codigo_user.get_profile().uploaded_photos,))
                else:
                    form = VerifyVotosForm(request.POST)
                    if form.is_valid():
                        pattern = form.cleaned_data['pattern']
                    else:
                        pattern = ""
                    u = v.codigo_user
                    p = v.codigo_user.get_profile()
                    if re.search(pattern,u.username) or re.search(
                        pattern,u.email) or re.search(
                        pattern,u.first_name) or re.search(
                        pattern,u.last_name) or re.search(pattern,p.sexo):
                        if not pais_id or (pais_id and (int(p.pais.numcode) == int(pais_id))):
                            profiles.append((v.codigo_user.username, v.codigo_user.email,
                                             v.codigo_user.first_name, v.codigo_user.last_name,
                                             v.codigo_user.get_profile().fecha_nacimiento,
                                             v.codigo_user.get_profile().sexo,
                                             v.codigo_user.get_profile().pais,
                                             v.codigo_user.get_profile().departamento,
                                             v.codigo_user.get_profile().uploaded_photos,))

                    
        profiles.sort(key = lambda fecha_nacimiento: fecha_nacimiento[4])

    return direct_response(request, "admin/verify_votes/votes_list.html",
                           {"profiles_list": profiles, 
                            "countries_list": Country.objects.iterator(),
                            "foto_id": foto_id})

@staff_member_required
def disqualify_user(request):
    """
    inhabilita a un usuario, así como a todas sus fotos y votos
    """
    if request.method == 'POST':
        form =DesqualifyUserForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('admin_user_disqualified')
    return redirect('admin_verify_votes')


# @staff_member_required
# def show_all_votes_patterns(request, foto_id):
#     """
#     muestra una página con todos los datos de los usuarios que votaron por la foto en la temporada actual de votación, estos usuarios contienen en alguno de campos el patron "pattern" 
#     """
# #    if request.method == 'GET':

#     foto=get_object_or_404(Foto, pk=int(foto_id))
#     temporada=Temporada().get_Current_Voting_Temporada()
#     profiles = []
#     if temporada:
#         for v in foto.voto_set.filter(codigo_temporada=temporada).filter(alive=True):
#             if not pattern:
#                 profiles.append((v.codigo_user.username, v.codigo_user.email,
#                                  v.codigo_user.first_name, v.codigo_user.last_name,
#                                  v.codigo_user.get_profile().fecha_nacimiento,
#                                  v.codigo_user.get_profile().sexo,
#                                  v.codigo_user.get_profile().pais,
#                                  v.codigo_user.get_profile().departamento,
#                                  v.codigo_user.get_profile().uploaded_photos,))
#             else:
# #falta terminar esto y arreglarlo xq se ve horrible
#                 u = v.codigo_user
#                 p = v.codigo_user.get_profile()
#                 if re.search(pattern,u.username) or re.search(
#                     pattern,u.email) or re.search(
#                     pattern,u.first_name) or re.search(
#                     pattern,u.last_name) or re.search(
#                     pattern,p.fecha_nacimiento) or re.search(
#                     pattern,p.sexo) or re.search(pattern,p.uploaded_photos):
#                     profiles.append((v.codigo_user.username, v.codigo_user.email,
#                                      v.codigo_user.first_name, v.codigo_user.last_name,
#                                      v.codigo_user.get_profile().fecha_nacimiento,
#                                      v.codigo_user.get_profile().sexo,
#                                      v.codigo_user.get_profile().pais,
#                                      v.codigo_user.get_profile().departamento,
#                                      v.codigo_user.get_profile().uploaded_photos,))
#         profiles.sort(key = lambda fecha_nacimiento: fecha_nacimiento[4])

#     return direct_response(request, "admin/verify_votes/votes_list.html",
#                            {"profiles_list": profiles, 
#                             "countries_list": Country.objects.iterator(),
#                             "foto_id": foto_id})


# TODO: limitar el acceso a miembros del staff
#def estadisticas(request):
#    """
#    Muestra un conjunto de estadísticas generales de acceso a un miembro del 
#    staff
#    """
#    nro_fotos = Foto.objects.count()
#    nro_vistas = Foto.objects.aggregate(Sum('vistas'))
#    nro_usuarios = UserProfile.objects.count()
#    nro_favoritos = [user.favoritos.count() for user in UserProfile.objects.all()]
#    ranking = sorted(Foto.objects.all(), key=lambda foto:foto.fans.count(), reverse=True)[:10]
#    nro_comentarios = Comentario.objects.filter(estado=u"M").count()
#    
#    return direct_response(request, 'admin/estadisticas/estadisticas.html',
#                           {'nro_fotos': nro_fotos,
#                            'nro_vistas': nro_vistas['vistas__sum'],
#                            'nro_usuarios': nro_usuarios,
#                            'nro_favoritos': sum(nro_favoritos),
#                            'ranking': ranking,
#                            'nro_comentarios': nro_comentarios,
#                            })
                            

#@csrf_exempt
#def favoritas(request):
#    """
#    Devuelve las fotos favoritas, según el número que el administrador decide
#    """
#    if request.method == 'POST':
#        form = FavoritaForm(request.POST)
#        if form.is_valid():
#            fotos = Foto.objects.all().order_by("-fans")
#            favoritas = []
#            for foto in fotos:
#                repetida = False
#                for favorita in favoritas:
#                    if favorita['foto'].id == foto.id:
#                        repetida = True
#                if not repetida:
#                    favoritas.append({'foto': foto, 'fans': foto.fans.all()})
#            
#            return direct_response(request, "admin/estadisticas/favoritas.html",
#                                   {"form_lleno": True,
#                                    "favoritas": favoritas[:form.cleaned_data['numero']]})
#    else:
#        form = FavoritaForm()
#        
#    return direct_response(request, "admin/estadisticas/favoritas.html",
#                           {"form": form,
#                            "form_lleno": False})


#def ganadora_temporada(request, temporada_id=None):
#    """
#    Determina a los ganadores de una temporada
#    """
#    if temporada_id:
#        temporada = Temporada.objects.get(id=temporada_id)
#        ganadores = Foto.objects.filter(ganadora_temporada=temporada)
#        
#        return direct_response(request, "admin/estadisticas/ganadoras_temporada.html",
#                               {"temporada": temporada,
#                                "ganadores": ganadores,
#                                "eleccion": True})        
#    else:
#        temporadas = Temporada.objects.all()
#        
#        return direct_response(request, "admin/estadisticas/ganadoras_temporada.html",
#                               {"temporadas": temporadas,
#                                "eleccion": False})        


#def manage_db(request):
#    """
#    muestra la vista con las opciones de generar backup
#    """
#    return direct_response(request, 'admin/manage_db/manage_db.html')
#manage_db = staff_member_required(manage_db)

#def generar_backup(request):
#    """
#    Ejecuta el command.handle que realiza el backup de la base de datos.
#    """
#    create_backup = Command()
#    create_backup.handle()
#    return HttpResponseRedirect(reverse('admin_generar_backup_exito'))
#manage_db = staff_member_required(manage_db)
#
#def generar_backup_exito(request):
#    """
#    Muestra un mensaje indicando que se genero el backup con exito
#    """
#    return direct_response(request, 'admin/manage_db/backup_exito.html')
#manage_db = staff_member_required(manage_db)

#para que funcione hay que deshablitar el init de las fotos
#eso no es recomentable, ni esta probado
#def habilitar_fotos(request):
#    """
#    Asigna al atributo 'temporada_habilitado' de todas fotos el valor de 'S'
#    Lo cual las habilita para cualquier temporada, sin embargo no la modera
#    """
#    form = HabilitarFotosForm()
#    if request.method == 'POST':
#        form = HabilitarFotosForm(request.POST)
#        if form.is_valid():
#            form.save()
#            return HttpResponseRedirect(reverse('admin_habilitar_fotos_exito'))
#    return direct_response(request, "admin/habilitar_fotos/habilitar.html",
#                           {'form': form})

#le falta poner el template correcto
#@csrf_exempt
#def send_email(request):
#    """
#    Envía un mail a una lista de contactos
#    """
#    form = SendEmailForm()
#    if request.method == 'POST':
#        form = SendEmailForm(request.POST)
#        if form.is_valid():
#            msg = EmailMessage(__(u"Administrador de MP100"),
#                               form.cleaned_data['texto'],
#                               "info@machu-picchu100.com",
#                               form.cleaned_data['para'].split(","))
#            msg.send()
#            return HttpResponseRedirect(reverse('admin_enviar_email_exito'))
#
#    return direct_response(request, "admin/send_email/email_form.html",
#                           {'form': form})
