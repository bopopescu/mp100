# -*- coding: utf-8 -*-
from models import Noticia, Categoria, Temporada, BadgeImage, GranGanador, Foto, PanoramicWinner, ProfessionalWinner
from django.contrib import admin, messages
from django.conf.urls.defaults import *
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from forms import TemporadaAdminForm, GanadorFinalistaForm, PanoramicWinnerForm, ProfessionalWinnerForm
from common.utils import direct_response
import datetime

class CategoriaAdmin(admin.ModelAdmin):
    pass

#admin.site.register(Noticia)
admin.site.register(Categoria, CategoriaAdmin)

class TemporadaAdmin(admin.ModelAdmin):
    list_display=('titulo', 'fecha_inicio', 'fecha_fin')
    list_display_links=('titulo', 'fecha_inicio', 'fecha_fin')

    form = TemporadaAdminForm

    change_form_template = 'admin/temporada/change_form.html'
    add_form_template = 'admin/temporada/add_form.html'
    
    def change_view(self, request, object_id, extra_context=None):
        return super(self.__class__, self).change_view(request, object_id, extra_context={'temporada_id':object_id})
    
admin.site.register(Temporada, TemporadaAdmin)

class BadgeImageAdmin(admin.ModelAdmin):
    list_display=('id','vista_previa','name_en','name_es','description_en',
                  'description_es')
    list_display_links=('id','name_en','name_es','description_en',
                        'description_es')    
    exclude = ('height', 'width')
admin.site.register(BadgeImage, BadgeImageAdmin)

class GranGanadorAdmin(admin.ModelAdmin):
    list_display=('vista_previa', 'titulo_foto', 'comentario', 
                  'categoria_foto','winner')

    def get_urls(self):
        urls = super(GranGanadorAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^add/(?P<category_id>\d+)?$', 
                               self.add_winner,name='fotos_GranGanadorAdd')
                           )
        return my_urls + urls

    @never_cache
    def add_winner(self, request, category_id):
        """
        muestra una pagina con las fotos ganadoras de las 10 temporadas
        permitiendo seleccionar a las ganadoras finales
        """
        object_list = Foto.objects.filter(ganadora_temporada__isnull=False)
        FinalistasFormSet = formset_factory(GanadorFinalistaForm, 
                                            extra=0)
        if not category_id:
            category_id=0
        if request.method == 'GET':
            if int(category_id)!=0:
                object_list=object_list.filter(categoria__id=category_id)
        if request.method == 'POST':
            formset = FinalistasFormSet(request.POST)
            if int(formset.data['category'])!=0:
                object_list=object_list.filter(
                    categoria__id=int(formset.data['category']))
            if formset.is_valid():
                for form in formset.forms:
                    form.save()
                messages.info(request, 'Operación exitosa.')
                return HttpResponseRedirect('/admin/fotos/granganador/')
        else:
            li=[]
            selected=0
            comentario=''
            winner=0
            finalistas = GranGanador.objects.all()
            for f in object_list:
                query = finalistas.filter(codigo_foto=f)
                if query:
                    selected=1
                    comentario=query[0].comentario
                    winner=query[0].winner
                li.append( {'foto_id':f.id, 
                            'selected':selected, 
                            'comentario':comentario,
                            'winner':winner} )
                selected=0
                comentario=''
                winner=0
            formset=FinalistasFormSet(initial = li)
        return direct_response(request, "admin/granganador/add_form.html",
                               {"fotos_list": object_list,
                                "formset":formset,
                                "formset_list":formset.forms,
                                "category_list":Categoria.objects.all(),
                                "cat_id":int(category_id)})

admin.site.register(GranGanador, GranGanadorAdmin)

class PanoramicWinnerAdmin(admin.ModelAdmin):
    list_display=('vista_previa', 'titulo_foto', 'comentario', 
                  'categoria_foto', 'winner')

    def get_urls(self):
        urls = super(PanoramicWinnerAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^add/(?P<category_id>\d+)?$', 
                               self.add_winner,name='fotos_PanoramicWinnerAdd')
                           )
        return my_urls + urls

    @never_cache
    def add_winner(self, request, category_id):
        """
        Muestra una pagina con las fotos panoramicas subidas hasta la 
        temporada 10.
        Permitiendo seleccionar a las ganadoras finales
        """
        #considering all panoramics photos uploaded before the beginning of the
        #voting period 10, it was 2011-8-1 12:00:00 a.m.
        object_list = Foto.objects.filter(panoramica=True).filter(estado='M').filter(fecha__lt=datetime.datetime(2011,8,1,12,0,0))
        PanoramicsFormSet = formset_factory(PanoramicWinnerForm, 
                                            extra=0)
        if not category_id:
            category_id=0
        if request.method == 'GET':
            if int(category_id)!=0:
                object_list=object_list.filter(categoria__id=category_id)
        if request.method == 'POST':
            formset = PanoramicsFormSet(request.POST)
            if int(formset.data['category'])!=0:
                object_list=object_list.filter(
                    categoria__id=int(formset.data['category']))
            if formset.is_valid():
                for form in formset.forms:
                    form.save()
                messages.info(request, 'Operación exitosa.')
                return HttpResponseRedirect('/admin/fotos/panoramicwinner/')
        else:
            li=[]
            selected=0
            comentario=''
            winner=0
            finalistas = PanoramicWinner.objects.all()
            for f in object_list:
                query = finalistas.filter(codigo_foto=f)
                if query:
                    selected=1
                    comentario=query[0].comentario
                    winner=query[0].winner
                li.append( {'foto_id':f.id, 
                            'selected':selected, 
                            'comentario':comentario,
                            'winner':winner} )
                selected=0
                comentario=''
                winner=0
            formset=PanoramicsFormSet(initial = li)
        return direct_response(request, "admin/panoramicWinner/add_form.html",
                               {"fotos_list": object_list,
                                "formset":formset,
                                "formset_list":formset.forms,
                                "category_list":Categoria.objects.all(),
                                "cat_id":int(category_id)})

admin.site.register(PanoramicWinner, PanoramicWinnerAdmin)

###
class ProfessionalWinnerAdmin(admin.ModelAdmin):
    list_display=('vista_previa', 'titulo_foto', 'comentario', 'winner')

    def get_urls(self):
        urls = super(ProfessionalWinnerAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^add/$', 
                               self.add_winner,name='fotos_ProfessionalWinnerAdd')
                           )
        return my_urls + urls

    @never_cache
    def add_winner(self, request):
        """
        Muestra una pagina con las fotos panoramicas subidas hasta la 
        temporada 10.
        Permitiendo seleccionar a las ganadoras finales
        """
        #considering all professinal photos uploaded before the beginning of the
        #voting period 10, it was 2011-8-1 12:00:00 a.m.
        catPro = Categoria.objects.get(nombre='Professional')
        object_list = Foto.objects.filter(categoria=catPro).filter(estado='M').filter(fecha__lt=datetime.datetime(2011,8,1,12,0,0))
        ProfessionalsFormSet = formset_factory(ProfessionalWinnerForm, 
                                            extra=0)
        if request.method == 'POST':
            formset = ProfessionalsFormSet(request.POST)
            if formset.is_valid():
                for form in formset.forms:
                    form.save()
                messages.info(request, 'Operación exitosa.')
                return HttpResponseRedirect('/admin/fotos/professionalwinner/')
        else:
            li=[]
            selected=0
            comentario=''
            winner=0
            finalistas = ProfessionalWinner.objects.all()
            for f in object_list:
                query = finalistas.filter(codigo_foto=f)
                if query:
                    selected=1
                    comentario=query[0].comentario
                    winner=query[0].winner
                li.append( {'foto_id':f.id, 
                            'selected':selected, 
                            'comentario':comentario,
                            'winner':winner} )
                selected=0
                comentario=''
                winner=0
            formset=ProfessionalsFormSet(initial = li)
        return direct_response(request, 
                               "admin/professionalWinner/add_form.html",
                               {"fotos_list": object_list,
                                "formset":formset,
                                "formset_list":formset.forms,})

admin.site.register(ProfessionalWinner, ProfessionalWinnerAdmin)
