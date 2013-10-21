# -*- coding: utf-8 -*-

from django.contrib import admin
# models
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext as __
from base64 import urlsafe_b64encode
from MP100.fotos.models import *
from MP100.portal.models import Banner
from MP100.common.utils import sendHtmlMail, direct_response

class AdminFoto(admin.ModelAdmin):
    list_display = ("titulo", "codigo_user", "estado", "categoria", "panoramica", "num_favoritos", "vista_previa", "rechazo",)
    list_filter = ("categoria", "estado",)
    search_fields = ("=codigo_user__email",)
    list_editable = ("estado", "rechazo", "categoria", "panoramica",)
    list_per_page = 10
    readonly_fields = ('fecha', 'height', 'width', 'codigo_user', 'foto', 'vistas', 'ganadora_temporada',)
    ordering = ("-fecha",)
    fieldsets = (
        ('Opciones Avanzadas', {
            'fields': ("categoria", "estado", "titulo", "descripcion", )
        }),
        ('Otros datos', {
            'classes': ('collapse',),
            'fields': ('fecha', 'height', 'width', 'codigo_user', 'foto', 'vistas', 'ganadora_temporada',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """
        Si se cambió de categoría o la foto se colocó como panorámica
        se envía un mail al usuario
        """
        if change:
            user = UserProfile.objects.get(user=obj.codigo_user)
            photo = Foto.objects.get(id=obj.id)
            if photo.categoria != obj.categoria:
                data = {'user_firstname': obj.codigo_user.first_name,
                        'photo_title':obj.titulo,
                        'email': obj.codigo_user.email,
                        'mydomain': request.META['HTTP_HOST'],
                        'encryptedUsername': urlsafe_b64encode(str(obj.codigo_user.id))}
                if obj.codigo_user.get_profile().idioma == u'en':
                    subject = u"Machu Picchu 100 – Your photo has been recategorized"
                    data['category_name'] = obj.categoria.nombre
                    template='a-photo-recategorized_en.html'
                else:
                    subject = u"Machu Picchu 100 – Hemos cambiado la categoría de tu foto"
                    data['category_name'] = obj.categoria.nombre_espaniol
                    template='a-photo-recategorized_es.html'
                if user.accept_email_updates:
                    sendHtmlMail("info@machu-picchu100.com", subject,
                                 template,
                                 data, obj.codigo_user.email)

            #if obj.panoramica and not photo.panoramica:
            #    user = UserProfile.objects.get(user=obj.codigo_user)
            #    if user.idioma == u"es":
            #        subject = __(u"Su foto ha sido marcada como panorámica")
            #        data = (obj.codigo_user.get_full_name(),
            #                obj.titulo,)
            #        send_html_mail(subject, "cambio_panoramica_es.html", data,
            #                       "info@machu-picchu100.com",
            #                       [obj.codigo_user.email])
            #    else:
            #        subject = __(u"Su foto ha sido marcada como panorámica")
            #        data = (obj.codigo_user.get_full_name(),
            #                obj.titulo,)
            #        send_html_mail(subject, "cambio_panoramica_en.html", data,
            #                       "info@machu-picchu100.com",
            #                       [obj.codigo_user.email])

        obj.save()


class AdminComentario(admin.ModelAdmin):
    list_display = ("__unicode__", "texto", "estado")
    list_filter = ("estado",)
    list_editable = ("estado",)
    list_per_page = 10

    
#class AdminBanner(admin.ModelAdmin):
#    list_display = ("title", "country", "clicks", "vista_previa")
#    readonly_fields = ("clicks",)
#    ordering = ("country",)


class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("vista_previa", "razon", "comentario", "respuesta")
    list_display_links = ("vista_previa", "razon",)
    list_editable = ("respuesta",)
    ordering = ("respuesta",)
    list_per_page = 10
    def queryset(self, request):
        return Denuncia.objects.filter(respuesta=u'E')

class AdminKuna_photos(admin.ModelAdmin):
    
    add_form_template = 'admin/kuna_photos/change_list.html'
    
    def add_view(self, request, extra_context=None):
        return direct_response(request, "admin/kuna_photos/change_form.html",
                               {"fotos_list": Foto.objects.all(),})        

admin.site.register(UserProfile)
admin.site.register(Foto, AdminFoto)
#admin.site.register(Comentario, AdminComentario)
#admin.site.register(Banner, AdminBanner)
#admin.site.register(ComentarioPerfil)
admin.site.register(Denuncia, DenunciaAdmin)
admin.site.register(kuna_photos, AdminKuna_photos)

admin.site.disable_action('delete_selected')
