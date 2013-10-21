# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('servicios/templatetags/ser_preview.html')
def ser_preview(servicio, span_width="2,7"):
    """
    Muestra una vista previa de los servicios con detalles, se puede colocar
    un parámetro adicional para la maquetación con blueprint
    """
    (left, right) = span_width.split(",")
    
    return {'servicio': servicio,
            'left': left,
            'right': right}


@register.inclusion_tag('servicios/templatetags/ser_previewmin.html')
def ser_preview_min(servicio):
    """
    Muestra una vista previa de los servicios utilizada en varios templates
    """
    return {'servicio': servicio}


@register.inclusion_tag('servicios/templatetags/ser_pager.html')
def ser_paginator(paginated_list, label=""):
    """
    Muestra el paginador estandar para servicios de una lista paginada
    """
    return {'paginated_list': paginated_list,
            "label": "#%s" % label}