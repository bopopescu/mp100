#-*- coding: utf-8 -*-

from django import template
from MP100.ip2country.ip2country import IP2Country
from MP100.portal.models import Banner

register = template.Library()

def get_country(context):
    """
    Obtiene el país de origen del ip del cliente o retorna por defecto a Perú.
    """
    client_ip = context['request'].META['REMOTE_ADDR']
    ip2c = IP2Country(verbose=1)
    country = ip2c.lookup(client_ip)
    if country[0]:
        return country
    else:
        return ('PE', 'Peru')


@register.inclusion_tag('common/templatetags/banners.html', takes_context=True)
def banners(context, align):
    """
    Muestra los banners horizontales según el país
    """
    country = get_country(context)
    banners = Banner.objects.filter(country__iso=country, align=align).order_by("timer")
    
    return {'banners': banners, 'align': align}
    

@register.inclusion_tag('common/templatetags/banners_time.js', takes_context=True)
def get_ban_time(context, align):
    """
    Devuelve el número de banners de algún tipo
    """
    country = get_country(context)
    banners = Banner.objects.filter(country__iso=country, align=align).order_by("timer")
    
    return {'banners': banners, 'align': align}
