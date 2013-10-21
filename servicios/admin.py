#-*- coding: utf-8 -*-

from django.contrib import admin
from servicios.models import *


class AdministradorServicioAdmin(admin.ModelAdmin):
    """
    Administrador de servicio
    """
    list_display = ("servicio", "user",)
    readonly_fields = ("servicio", "user",)


class CaracteristicaAdmin(admin.ModelAdmin):
    """
    Característica
    """
    list_display = ("nombre", "tipo_servicio", "get_icono",)
    exclude = ("width", "height",)


class FotoAdmin(admin.ModelAdmin):
    """
    Admin para las fotos, se puede filtrar por servicios y moderados
    """
    list_display = ("nombre", "servicio", "moderado", "get_imagen",)
    list_editable = ("moderado",)
    list_filter = ("moderado", "servicio",)
    exclude = ("width", "height",)


class OpinionAdmin(admin.ModelAdmin):
    """
    Opinión
    """
    list_display = ("usuario", "servicio", "texto", "moderado")
    list_editable = ("moderado",)
    list_filter = ("moderado",)


class PuntajeAdmin(admin.ModelAdmin):
    """
    Puntajes de los usuarios a los servicios
    """
    list_display = ("servicio", "usuario", "puntuacion")


class RespuestaAdmin(admin.ModelAdmin):
    """
    Resultado
    """
    list_display = ("administrador", "texto",)


class ServicioAdmin(admin.ModelAdmin):
    """
    Servicio, se puede marcar a los servicios como destacados
    """
    list_display = ("nombre", "tipo_servicio", "estado", "destacado",
                    "puntuacion", "num_visitas", "get_foto", "get_ubicacion")
    list_editable = ("destacado", "estado")
    list_filter = ("tipo_servicio", "destacado", "estado")
    exclude = ("width", "height", "width_p", "height_p",)
    readonly_fields = ("num_visitas", "num_opiniones", "num_puntuaciones",
                       "puntuacion")


class SubtipoServicioAdmin(admin.ModelAdmin):
    """
    Subtipo de servicio
    """
    list_display = ("nombre", "tipo_servicio",)
    list_filter = ("tipo_servicio",)


class TipoServicioAdmin(admin.ModelAdmin):
    """
    Tipo de servicio
    """
    list_display = ("nombre", "get_icono",)
    exclude = ("width", "height",)


class UbicacionAdmin(admin.ModelAdmin):
    """
    Ubicacion de un servicio
    """
    list_display = ("direccion", "get_map",)


class ActividadAdmin(admin.ModelAdmin):
    """
    Stream de actividades
    """
    list_display = ("get_str", "fecha")


admin.site.register(Ubicacion, UbicacionAdmin)
admin.site.register(TipoServicio, TipoServicioAdmin)
admin.site.register(SubtipoServicio, SubtipoServicioAdmin)
admin.site.register(Caracteristica, CaracteristicaAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(AdministradorServicio, AdministradorServicioAdmin)
admin.site.register(Respuesta, RespuestaAdmin)
admin.site.register(Opinion, OpinionAdmin)
admin.site.register(Puntaje, PuntajeAdmin)
admin.site.register(Foto, FotoAdmin)
admin.site.register(Actividad, ActividadAdmin)
admin.site.register(UbicacionComun)
