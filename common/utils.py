# -*- coding: utf-8 -*-

import codecs
from django.conf import settings
from django.core.mail import EmailMessage, BadHeaderError, \
    EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
try:
    from django.template.base import Template
except:
    from django.template import Template
from django.utils import simplejson, encoding
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from random import Random
import string


def direct_response(request, *args, **kwargs):
    """
    Forma resumida de render_to_response, enviando context_instance al template
    """
    kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)


def json_response(data):
    """
    Devuelve una respuesta json con la información de data
    """
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def sendHtmlMail(from_email, subject, templateName, data, to_, text_content='',
                 path='portal/email_templates/'):
    """
    envia un correo con un template en html,
    data es un diccionario
    """
    try:
        context = Context(data)
        html_content = mark_safe(render_to_string(
            '%s%s' % (path, templateName), context))
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except:
        a=1

def send_html_mail(subject, html_file, data, from_email, to_emails, files=None):
    """
    Envía un e-mail con contenido html el cual es extraído de un archivo de 
    codificación utf-8 ubicado en MEDIA_URL/html colocando la data correcta, 
    la cual debe ser una lista, como parámetro opcional se pueden poner archivos
    adjuntos en forma de lista
    """
    html = codecs.open('%shtml/%s' % (settings.MEDIA_ROOT, html_file), "r",
                       "utf-8")
    content = mark_safe(html.read() % data)
    html.close()

    try:
        msg = EmailMessage(subject, content, from_email, to_emails)
        msg.content_subtype = "html"
        if files:
            for afile in files:
                msg.attach_file(afile)
        else:
            pass
        msg.send()

    except BadHeaderError:
        return HttpResponse('Se encontró una cabecera de e-mail inválida')
        

def get_paginated(request, object_list, num_items):
    """
    Devuelve una lista paginada de una lista de objetos y el
    número de objetos por página
    """
    paginator = Paginator(object_list, num_items)   
         
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1        
        
    try:
        lista_paginada = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lista_paginada = paginator.page(paginator.num_pages)
        
    return lista_paginada
    
    
def make_password(length=8):
    """
    Devuelve una cadena aleatoria de tamaño length
    """
    return ''.join(Random().sample(string.letters+string.digits, length))


def convert_unicode_to_string(x):
   """
   >>> convert_unicode_to_string(u'ni\xf1era')
   'niera'
   """
   return encoding.smart_str(x, encoding='ascii', errors='ignore')


def json_fastsearch(queryset, search_field, substring, fields):
    """
    Realiza una fastsearch dentro de una tabla retornando un diccionario json
    con los atributos seleccionados enviando los nombres correctos en forma de
    diccionario con el siguiente formato
    {"id": "id",
    "name": "nombre",
    "description": "descripcion",
    "image": "foto"}
    """
    filter = "%s__icontains" % search_field
    match_list = queryset.filter(**{filter: substring})
    json_dict = []
    for object in match_list:
        json_dict.append(
                {"id": getattr(object, fields["id"]),
                 "name": getattr(object, fields["name"]),
                 "subtitle": getattr(object, fields["subtitle"]).nombre,
                 "description": getattr(object, fields["description"]),
                 "image": getattr(object, fields["image"]).generate_url("icon")})

    return json_response(json_dict)


def get_object_or_none(Model, *args, **kwargs):
    """
    Retorna el objeto o None en caso de que no exista este
    """
    try:
        Model.objects.get(*args, **kwargs)
        return Model.objects.get(*args, **kwargs)
    except Model.DoesNotExist:
        return None
