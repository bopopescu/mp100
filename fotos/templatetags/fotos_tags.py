from django import template
from django.contrib.auth.models import User
from MP100.fotos.models import Temporada, Voto, BadgeImage
from datetime import datetime

#tag {% get_some_user_fotos user 5 as user_fotos order owner %}

def do_some_user_fotos(parser, token):
    bits = token.split_contents()
    if len(bits) != 7:
       raise template.TemplateSyntaxError("el tag 'get_some_user_fotos' toma exactamente 6 argumentos ")
    return SomeUserFotosNode(bits[1], bits[2], bits[4], bits[5], bits[6])
    
class SomeUserFotosNode(template.Node):
    """
        retorna un numero de fotos igual a num_fotos, 
        si order == 1, retorna las fotos ordenas por id en forma ascendente
        si order == -1, retorna las fotos en orden descendente
        si owner == 1, retorna todas las fotos del usuario, incluso
                        aquellas que esten en proceso de moderacion
    """    
    def __init__(self, user, num_fotos, varname, order, owner):
        self.user = template.Variable(user)
        self.num_fotos = int(num_fotos)
        self.varname = varname
        self.order = int(order)
        self.owner = int(owner)
        
    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        if self.owner == 1 :
            if self.order == 1:
                context[self.varname] = user.fotos.order_by('id')[:self.num_fotos]
            else:
                context[self.varname] = user.fotos.order_by('-id')[:self.num_fotos]        
        else:
            if self.order == 1:
                context[self.varname] = user.fotos.filter(estado='M').filter(temporada_habilitado='S').order_by('id')[:self.num_fotos]
            else:
                context[self.varname] = user.fotos.filter(estado='M').filter(temporada_habilitado='S').order_by('-id')[:self.num_fotos]
        return ''

        
register = template.Library()
register.tag('get_some_user_fotos', do_some_user_fotos)

#tag {% get_some_friends_fotos user 4 as friend_fotos %}
def do_some_friends_fotos(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
       raise template.TemplateSyntaxError("el tag 'get_some_friends_fotos' toma exactamente 4 argumentos ")
    return SomeFriendsFotosNode(bits[1], bits[2], bits[4])        

class SomeFriendsFotosNode(template.Node):
    """
        retorna un numero de userprofile de amigos igual a num_fotos,
        ordenados por -id
    """
    def __init__(self, user, num_fotos, varname):
        self.user = template.Variable(user)
        self.num_fotos = int(num_fotos)
        self.varname = varname
        
    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.varname] = user.get_profile().amigos.order_by('-id')[:self.num_fotos]      
        return ''

register.tag('get_some_friends_fotos', do_some_friends_fotos)

#tag {% get_some_friend_requests user 4 as friend_requests %}
def do_some_friend_requests(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
       raise template.TemplateSyntaxError("el tag 'get_some_friends_requests' toma exactamente 4 argumentos ")
    return SomeFriendRequestsNode(bits[1], bits[2], bits[4])        

class SomeFriendRequestsNode(template.Node):
    """
        retorna un numero de solicitudes de amistad igual a num,
        ordenados por -id
    """
    def __init__(self, user, num, varname):
        self.user = template.Variable(user)
        self.num = int(num)
        self.varname = varname
        
    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.varname] = user.solicitudes.order_by('-id')[:self.num]      
        return ''

register.tag('get_some_friend_requests', do_some_friend_requests)


#tag {% get_my_votes user temp as my_votes %}
def do_my_votes(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
       raise template.TemplateSyntaxError("el tag 'get_my_votes' toma exactamente 4 argumentos ")
    return MyVotesNode(bits[1], bits[2], bits[4])
    
class MyVotesNode(template.Node):
    """
        retorna un numero de fotos por las que se voto el usuario
        en la temporada temp
    """
    def __init__(self, user, temp, varname):
        self.user = template.Variable(user)
        self.temp = template.Variable(temp)
        self.varname = varname
        
    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        try:
            temp = self.temp.resolve(context)
        except template.VariableDoesNotExist:
            return ''
    
        temp_votes = Voto.objects.filter(codigo_temporada=temp).filter(codigo_user=user)
        fotos=[]
        for v in temp_votes:
            fotos.append(v.codigo_foto)
        context[self.varname]=fotos
        return ''

register.tag('get_my_votes', do_my_votes)

#tag {% get_ganadores_temporadas 4 as temp_winners %}
def do_ganadores_temporadas(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
       raise template.TemplateSyntaxError("el tag 'get_ganadores_temporadas' toma exactamente 3 argumentos. ")
    return GanadoresTemporadasNode(bits[1], bits[3])
    
class GanadoresTemporadasNode(template.Node):
    """
        retorna un numero usuarios, aquellos que ganaron la temporada mas cercana,
        igual a num_fotos
    """
    def __init__(self, num_fotos, varname):
        self.num_fotos = int(num_fotos)
        self.varname = varname
        
    def render(self, context):
        temporadas = Temporada.objects.all()
        if temporadas:
            tmp=temporadas[0].get_last_temporada()
            if tmp:
                usuarios = []
                for foto in tmp.foto_set.all()[:self.num_fotos]:
                    usuarios.append(foto.codigo_user)
                context[self.varname] =  usuarios
        return ''

register.tag('get_ganadores_temporadas', do_ganadores_temporadas)

#tag {% get_all_next_temporadas user temporadas %}
def do_all_next_temporadas(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
       raise template.TemplateSyntaxError("el tag 'get_all_nexttemporadas' toma exactamente 2 argumentos. ")
    return AllNextTemporadasNode(bits[1], bits[2])
    
class AllNextTemporadasNode(template.Node):
    """
        retorna una lista de todas las temporadas siguientes
        si no hay ninuga retorna ""
    """    
    def __init__(self, user, varname):
        self.varname = varname
        self.user = template.Variable(user)
        
    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.varname] = Temporada.objects.order_by('fecha_inicio').filter(fecha_inicio__gt=datetime.now())
        return ''

register.tag('get_all_next_temporadas', do_all_next_temporadas)

#tag {% get_current_badge user as badge  %}
def do_get_current_badge(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
       raise template.TemplateSyntaxError("el tag 'get_current_badge' toma exactamente 4 argumentos ")
    return GetCurrentBadgeNode(bits[1], bits[3])

class GetCurrentBadgeNode(template.Node):
    """
    retorna el ultimo objeto BadgeImage que gano el usuario 'user'
    """
    def __init__(self, user, varname):
        self.user = template.Variable(user)
        self.varname = varname

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.varname] = user.get_profile().get_BadgeImage()
        return ''

register.tag('get_current_badge', do_get_current_badge)

#tag {% get_current_level user as level  %}
def do_get_current_level(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
       raise template.TemplateSyntaxError("el tag 'get_current_level' toma exactamente 4 argumentos ")
    return GetCurrentLevelNode(bits[1], bits[3])

class GetCurrentLevelNode(template.Node):
    """
    retorna el actual nivel del usuario 'user'
    """
    def __init__(self, user, varname):
        self.user = template.Variable(user)
        self.varname = varname

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        context[self.varname] = user.get_profile().get_level()
        return ''

register.tag('get_current_level', do_get_current_level)

#tag {% get_all_badges as badges  %}
def do_get_allBadges(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
       raise template.TemplateSyntaxError("el tag 'get_all_badges' toma exactamente 3 argumentos ")
    return GetAllBadgesNode(bits[2])

class GetAllBadgesNode(template.Node):
    """
    retorna una lista de todos los objetos BadgeImage
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = BadgeImage.objects.all()
        return ''

register.tag('get_all_badges', do_get_allBadges)

#{% get_object forloop.counter0 from fotos_list as foto %}
def do_get_object(parser, token):
    bits = token.split_contents()
    if len(bits) != 6:
       raise template.TemplateSyntaxError("el tag 'get_foto' toma exactamente 5 argumentos ")
    return GetObjectNode(bits[1], bits[3],bits[5])

class GetObjectNode(template.Node):
    """
    retorna el objeto especificado de la lista
    """
    def __init__(self, posicion, lista, objeto):
        self.posicion = template.Variable(posicion)
        self.lista = template.Variable(lista)
        self.objeto = objeto

    def render(self, context):
        try:
            posicion = self.posicion.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        try:
            lista = self.lista.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        if posicion < len(lista):
            context[self.objeto] = lista[posicion]
        else:
            context[self.objeto] = ''
        return ''

register.tag('get_object', do_get_object)
