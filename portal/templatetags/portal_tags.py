# -*- coding: utf-8 -*-
from django import template
from datetime import datetime, timedelta
from math import floor
from MP100.fotos.models import Temporada
from zinnia.models import Category, Entry

#tag {% get_temporadas temporadas %}
def do_temporadas(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
       raise template.TemplateSyntaxError("el tag 'get_temporadas' toma exactamente 1 argumento. ")
    return TemporadasNode(bits[1])
    
class TemporadasNode(template.Node):
    """
        retorna una lista de todas las temporadas
    """    
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = Temporada.objects.order_by('-fecha_inicio')
        return ''

        
register = template.Library()
register.tag('get_temporadas', do_temporadas)

#tag {% get_actual_and_next_temporadas actual_temp next_temp %}
def do_actual_and_next_temporadas(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
       raise template.TemplateSyntaxError("el tag 'get_actual_and_next_temporadas' toma exactamente 2 argumentos. ")
    return ActualNextTemporadasNode(bits[1], bits[2])
    
class ActualNextTemporadasNode(template.Node):
    """
    retorna la temporada actual y la siguiente inmediata
    en caso no exista alguna se retorna ''
    """
    def __init__(self, varname1, varname2):
        self.varname1 = varname1
        self.varname2 = varname2
        
    def render(self, context):
        temporada = Temporada()
        context[self.varname1] = ''
        context[self.varname2] = ''
        Current = temporada.get_current_temporada()
        if Current:
            if Current.is_in_this_temporada(datetime.now()):
                context[self.varname1] = Current
            else:
                context[self.varname2] = Current
            if context[self.varname2] == '':
                context[self.varname2] = temporada.get_temporada_for(Current.fecha_fin)
        return ''        
register.tag('get_actual_and_next_temporadas', do_actual_and_next_temporadas)        
        
#tag {% filter_by_language language object_list new_object_list %}
def do_filter_by_language(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
       raise template.TemplateSyntaxError("el tag 'filter_by_language' toma exactamente 3 argumentos. ")
    return FilterByLanguage(bits[1], bits[2], bits[3])
    
class FilterByLanguage(template.Node):
    """
    recibe un object_list y los retorna filtrado por el idioma
    """
    def __init__(self, language, object_list, new_object_list):
        self.object_list = template.Variable(object_list)
        self.language = template.Variable(language)
        self.new_object_list = object_list
        
    def render(self, context):
        try:
            object_list = self.object_list.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        try:
            language = self.language.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        li = []
        for e in object_list:
            if e.categories.filter(slug=str(language)):
                li.append(e)
        context[self.new_object_list] = li
        return ''        
register.tag('filter_by_language', do_filter_by_language)        

#tag {% get_age birthday as years %}
def do_get_age(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
       raise template.TemplateSyntaxError("el tag 'get_age' toma exactamente 3 argumentos. ")
    return GetAgeNode(bits[1], bits[3])
    
class GetAgeNode(template.Node):
    """
    recibe una fecha y retorna la diferencia en anios con la fecha actual
    """
    def __init__(self, birthday, years):
        self.birthday = template.Variable(birthday)
        self.years = years
        
    def render(self, context):
        try:
            birthday = self.birthday.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        if birthday:
            years = int(floor((datetime.now().date()-birthday).days/365))
            context[self.years] = years
        return ''        
register.tag('get_age', do_get_age)        

