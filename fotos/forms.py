#-*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django import forms
from django.forms import ModelForm
from django.forms.widgets import RadioSelect
from django.http import HttpResponse
from django.core.files.images import get_image_dimensions
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader, Context
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from models import UserProfile, Solicitud_de_Amistad, Foto, Comentario, Temporada, Categoria, GranGanador, PanoramicWinner, ProfessionalWinner
from MP100.portal.forms import SearchFilterForm
from MP100.countries.models import Country
import shutil
import os, re

from models import UserProfile, Solicitud_de_Amistad, Foto, Comentario  

class ComentarioForm(forms.ModelForm):
    """
    Formulario para la subida de comentarios por los usuarios
    """
    class Meta:
        model = Comentario
        fields = ("texto",)      

class CompartirFotoForm(forms.Form):
    """
    Formulario para compartir el url de una foto por mail
    """
    email = forms.EmailField(label=u"e-mail")
    asunto = forms.CharField(widget=forms.Textarea)        

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class UserProfileForm(ModelForm):    
    tipo_titulo = ( 
        (u'Mr.', _(u"Mr")),
        (u'Mrs.', _(u"Mrs")),
        (u'Ms.', _(u"Ms")),
        (u'Miss.',_(u"Miss")),
        (u'Dr.',_(u"Dr")),        
    )
    tipo_sexo=((u'F',_(u'Femenino')),
                (u'M',_(u'Masculino')),)    
    foto = forms.ImageField(label='Photo', required=False,
                            widget=forms.FileInput(attrs={'class':'texbox special_gray',}))
    titulo = forms.ChoiceField(label='Title', widget=forms.Select(attrs={'class':'textbox special_gray',}), choices=tipo_titulo)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': "textbox special_gray", 'maxt_length':'50',}))
    last_name  = forms.CharField(widget=forms.TextInput(attrs={'class': "textbox special_gray", 'maxt_length':'50',}))
    #email = forms.EmailField(label='Correo', max_length=75)
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class': "textbox special_gray", 'readonly':"readonly", 'maxt_length':'50',}))
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'class': "textbox special_gray calendar",}, format = '%d-%m-%Y'),
                                       input_formats=('%d-%m-%Y',),
                                       help_text='(dd-mm-aaaa)')
    username = forms.CharField(label='Screen Name', widget=forms.TextInput(attrs={'class': "textbox special_gray", 'maxt_length':'50',}))
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    sexo = forms.ChoiceField(label='Gender',widget=forms.RadioSelect(renderer=HorizRadioRenderer), choices=tipo_sexo)
    pais = forms.ModelChoiceField(queryset=Country.objects.all(), label="Country Residence",
                                  widget=forms.Select(attrs={'class':'textbox special_gray',} ))
    LANGUAGE_CHOICES = (
        (u"en", _(u"English")),
        (u"es", _(u"Spanish")),
    )
    idioma = forms.ChoiceField(label="Language",
                               widget=forms.RadioSelect(renderer=HorizRadioRenderer),
                               choices=LANGUAGE_CHOICES)
    password1 =forms.CharField(label='New Password', required=False,
                               widget=forms.PasswordInput(attrs={'class':'textbox special_gray',}),
                               max_length=11, min_length=6,
                               error_messages={'max_length': 'El password no debe contener más de 11 caracteres',
                                               'min_length': "El password no debe contener menos de 6 caracteres"},)
    password2 =forms.CharField(label='Confirm New Password', required=False,
                               widget=forms.PasswordInput(attrs={'class':'textbox special_gray',}),
                               max_length=11, min_length=6,
                               error_messages={'max_length': 'El password no debe contener más de 11 caracteres',
                                               'min_length': "El password no debe contener menos de 6 caracteres"},)
    class Meta:
        model = UserProfile
        exclude = ['user', 'height', 'width','me_gusta_temp',]

    #def __init__(self, *args, **kwargs):
    #    super(self.__class__, self).__init__(*args, **kwargs)
    #    self.fields.keyOrder = ['user_id', 'foto', 'first_name', 'last_name',
    #                            'email', 'username', 'fecha_nacimiento',
    #                            'sexo', 'pais',]
      
    def save(self, user):
        """
            Guarda todos los cambios realizados y evita que el usuario
            tenga subida mas de una imagen en su carpeta perofil/[user.id]
        """
        user_profile = user.get_profile()     
        if os.path.exists(settings.MEDIA_ROOT+settings.USERPROFILE_PHOTO_PATH+str(user.id)+'/') and self.cleaned_data['foto']:
            shutil.rmtree(settings.MEDIA_ROOT+settings.USERPROFILE_PHOTO_PATH+str(user.id)+'/')
        user_profile.set(self.cleaned_data['foto'],
                         self.cleaned_data['fecha_nacimiento'],
                         self.cleaned_data['sexo'],
                         self.cleaned_data['titulo'],
                         self.cleaned_data['pais'],
                         self.cleaned_data['idioma'],
                         self.cleaned_data['departamento'],
                         )
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if(self.cleaned_data['password1']):
            user.set_password(self.cleaned_data['password1'])
        #return HttpResponse('%s x %s' % (user_profile.width, user_profile.height))

        user_profile.save()
        user.save()
        return self;

    def is_valid(self):
        """"
            Redefine el is_valid() y aumenta la validacion del tamanio
            de la imagen
        """
        result = super(self.__class__, self).is_valid()       
        if result:
            if self.cleaned_data['foto']:
                (width,height) = get_image_dimensions(self.cleaned_data['foto'])
                if not (width <= 1600 and height <= 1600):
                    return (False, _(u'Image dimensions must be equal o smaller than 1600 x 1600 px'))
                #restriccion de tamanio minimo
                #if (width * height < 2000000):
                #    return (False, 'La imagen debe tener como mínimo 2 Mega Pixeles')
                #restriccion de tamanio maximo
                #pendiente
                #restriccion de peso
                #pendiente
        return (result, '')

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'Las contraseñas no son iguales.'))
        return self.cleaned_data
            
    def clean_email(self):
        query = User.objects.all()
        user = query.filter(id=self.data['user_id'])
        #user = query.filter(id=self.cleaned_data['user_id'])
        if user[0].email == self.cleaned_data['email']:
            return self.cleaned_data['email']
        if not query.filter(email=self.cleaned_data['email']):
            return self.cleaned_data['email']
        raise forms.ValidationError('Este correo ya está registrado.')


class SubirFotoForm(ModelForm):
    
    codigo_user = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Foto
        #exclude = ['fans', 'vistas', 'escogida', 'codigo_user']
        exclude = ['vistas', 'escogida', 'codigo_user']
        
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [ 'codigo_user','foto', 'titulo', 'categoria', 'descripcion',]

    def save(self):
        """
            crea un nuevo registro de foto al respectivo usuario
        """
        user = User.objects.get(id=self.cleaned_data['codigo_user'])
        user.fotos.create(foto=self.cleaned_data['foto'],
                          titulo=self.cleaned_data['titulo'],
                          categoria=self.cleaned_data['categoria'],
                          descripcion=self.cleaned_data['descripcion'],)
        return self
                   
    def is_valid(self):
        """"
            Redefine es is_valid() y aumenta la validacion del tamanio
            de la imagen
        """
        result = super(self.__class__, self).is_valid()
        if result:
            (width,height) = get_image_dimensions(self.cleaned_data['foto'])
            if not (width >= 1600 or height >= 1600):
                return (False, 'La imagen debe tener algún lado de\
                        1600 píxeles como mínimo')
        return (result, '')
        
    

        
class SearchInviteFilterForm(SearchFilterForm):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['texto', 'pais',]
       
    def apply_filters(self, user_list):
        """Aplica los filtros correspondientes según los campos
        seleccionados.
        Requiere que toda la data este validada."""
        return super(self.__class__, self).apply_filters(user_list)

class SearchDeleteFriends(SearchFilterForm):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['texto', 'pais',]
       
    def apply_filters(self, amigos_list):
        """Aplica los filtros correspondientes según los campos
        seleccionados.
        Requiere que toda la data este validada."""
        if self.cleaned_data['texto'] and self.cleaned_data['pais']:
            return amigos_list.filter(Q(pais = self.cleaned_data['pais']) & (Q(user__username__icontains = self.cleaned_data['texto']) | Q(user__first_name__icontains = self.cleaned_data['texto']) | Q(user__last_name__icontains = self.cleaned_data['texto'])))
        if self.cleaned_data['texto']:
            return amigos_list.filter(Q(user__username__icontains = self.cleaned_data['texto']) | Q(user__first_name__icontains = self.cleaned_data['texto']) | Q(user__last_name__icontains = self.cleaned_data['texto']))
        if self.cleaned_data['pais']:
            return amigos_list.filter(pais = self.cleaned_data['pais'])
        return amigos_list    
        
class SearchPhotosForm(SearchFilterForm):
    texto = forms.CharField(label='Cuyo título o descripción contengan:' ,
                            max_length=50,
                            required = False,
                            widget=forms.TextInput(attrs={'class':'textbox special_gray search clearInput',
                                                          'value':_(u'Search Photos'),
                                                          'title':_(u'Search Photos'),}),)
    categoria = forms.ModelChoiceField(label=u'Por categoría',
                                       queryset=Categoria.objects.all(),
                                       empty_label=u'---------',
                                       required=False,
                                       widget=forms.Select(attrs={'class':'styled special_gray'}),)
    
    class Meta:
        exlude = ['pais']

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['texto', 'categoria']
        
    def apply_filters(self, fotos_list):
        """Aplica a fotos_list(que es un QuerySet) el filtrado por 
        titulo, descripcion"""
        qTitulo = Q(titulo__icontains = self.cleaned_data['texto'])
        qDescripcion = Q(descripcion__icontains = self.cleaned_data['texto'])
        qCategoria = Q(categoria = self.cleaned_data['categoria'])
        qUserName = Q(codigo_user__username = self.cleaned_data['texto']) 
        qFirstName = Q(codigo_user__first_name = self.cleaned_data['texto']) 
        qLastName = Q(codigo_user__last_name = self.cleaned_data['texto'])
        qEmail = Q(codigo_user__email = self.cleaned_data['texto']) 

        if self.cleaned_data['texto'] and self.cleaned_data['categoria']:
            if self.cleaned_data['texto'] != _(u'Search Photos'):
                return fotos_list.filter((qTitulo | qDescripcion | qUserName | qFirstName | qLastName | qEmail) & qCategoria)
            else:
                return fotos_list.filter(qCategoria)
        
        if self.cleaned_data['texto']:
            if self.cleaned_data['texto'] != _(u'Search Photos'):
                return fotos_list.filter(qTitulo | qDescripcion | qUserName | qFirstName | qLastName | qEmail)

        return fotos_list        

class DeleteCommentForm(forms.Form):
    comentario_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def clean_comenario_id(self):
        """
            Verifica que la data no haya sido modificada y este dentro del rango
            actual de comentarios.
        """
        try:
            Comentario.objects.get(id = self.cleaned_data['comentario_id'])
        except Comentario.DoesNotExist:
            raise forms.ValidationError("No modifique los campos.")
        return self.cleaned_data['comentario_id']
        
    def delete(self):
        """
            Borra el comentario
        """
        comment = Comentario.objects.get(id = self.cleaned_data['comentario_id'])
        comment.delete()


class DeletePhotoForm(forms.Form):
    foto_id = forms.IntegerField(widget=forms.HiddenInput())

    def is_valid(self, user):
        """
            Verifica que el id no haya sido alterado y que este dentro
            del rango de fotos
        """
        result = super(self.__class__, self).is_valid()
        if result:
            if not Foto.objects.filter(id = self.cleaned_data['foto_id']):
                result = False
        return result
    
    def delete_thumbnails_files(self, re_exp, dir):
        """
            Borra los archivos thumbnails que cumplen con la expresion regular
            re_exp y que estan dentro del path dir
        """
        for f in os.listdir(dir):
            if re.search(re_exp, f):
                os.remove(os.path.join(dir, f))
        return self

    def delete(self, user):
        """
            Remueve la relacion con el usuario actual,
            remueve la relacion con la categoria asociada,
            borra el registro foto
            y borra el archivo foto funtos con sus thumbnails generados.
        """
        foto = Foto.objects.get(id = self.cleaned_data['foto_id'])
        user.fotos.remove(foto)
        foto.categoria.foto_set.remove(foto)
        #divide el path de la foto y saca el ultimo elementos de la lista
        #que correspone al nombre de la imagen
        foto_name=foto.foto.url.split('/').pop()
        foto.delete()
        self.delete_thumbnails_files(r'\b'+foto_name+r'.(\d{3}|\d{2})x(\d{3}|d{2})\w+', settings.MEDIA_ROOT+settings.USERPHOTOS_FOLDER_PATH+str(user.id)+'/')
        return self
         
class AddFriendForm(forms.Form):   
    amigo = forms.IntegerField(widget=forms.HiddenInput())
    
    def save(self, user):
        new_solicitud = Solicitud_de_Amistad(codigo_user = User.objects.get(id=self.cleaned_data['amigo']),
                                             codigo_user_solicitante = user)
        new_solicitud.save()
        return new_solicitud
        
    def is_valid(self, user):
        """Verifica que id del amigo no este alterado y este dentro del
        rango de usuarios registrados. Tambien que no se este invitando
        ha si mismo"""
        result = super(self.__class__, self).is_valid()
        if result:
            if not User.objects.filter(id = self.cleaned_data['amigo']):
                result = False
            if user.id == self.cleaned_data['amigo']:
                result = False
        return result
    
    def requires_solicitude(self, user):
        """verifica que no se tiene ya una invitacion y que
        todavia no son amigos"""
        amigo = User.objects.get(id=self.cleaned_data['amigo'])
        result = True
        for user_amigo in amigo.solicitudes.all():
            if user == user_amigo.codigo_user_solicitante:
                result = False
        for user_amigo in user.solicitudes.all():
            if amigo == user_amigo.codigo_user_solicitante:
                result = False
        if amigo.get_profile() in user.get_profile().amigos.all():
            result = False
        return result

class DeleteFriendForm(forms.Form):   
    amigo = forms.IntegerField(widget=forms.HiddenInput())
           
    #FALTA EL BUSCAR AMIGOS (SOLO POR ICONTAINS_NOMBRE)
    def is_valid(self, user):
        """Verifica que id del amigo no este alterado y este dentro del
        rango de usuarios registrados. Tambien que no se este eliminando
        ha si mismo y que haiga seleccionado a uno de sus amigos"""
        result = super(self.__class__, self).is_valid()
        if result:
            if not User.objects.filter(id = self.cleaned_data['amigo']):
                result = False
            if user.id == self.cleaned_data['amigo']:
                result = False
            if not user.get_profile().amigos.filter(id = self.cleaned_data['amigo']):
                result = False
        return result

    def delete(self, user):
        amigo = User.objects.get(id=self.cleaned_data['amigo'])
        user.get_profile().amigos.remove(amigo.get_profile())
        return self
    
class DeleteSolicitude(forms.Form):
    amigo = forms.IntegerField(widget=forms.HiddenInput())
    
    def is_valid(self):
        """
        Verifica que id del amigo no este alterado y este dentro del
        rango de usuarios registrados.
        """
        result = super(self.__class__, self).is_valid()
        if result:
            if not User.objects.filter(id = self.cleaned_data['amigo']):
                result = False
        return result
    
    def delete(self, user):
        """
            Elimina la solicitud
        """
        solicitud = Solicitud_de_Amistad.objects.get(Q(codigo_user__id = user.id) & Q(codigo_user_solicitante__id = self.cleaned_data['amigo']))
        user.solicitudes.remove(solicitud)
        solicitud.delete()
        return self
        
class AcceptSolicitude(forms.Form):
    amigo = forms.IntegerField(widget=forms.HiddenInput())

    def is_valid(self):
        """
        Verifica que id del amigo no este alterado y este dentro del
        rango de usuarios registrados.
        """
        result = super(self.__class__, self).is_valid()
        if result:
            if not User.objects.filter(id = self.cleaned_data['amigo']):
                result = False
        return result
    
    def delete(self, user):
        """
            Elimina la solicitud
        """
        solicitud = Solicitud_de_Amistad.objects.get(Q(codigo_user__id = user.id) & Q(codigo_user_solicitante__id = self.cleaned_data['amigo']))
        user.solicitudes.remove(solicitud)
        solicitud.delete()
        return self
      
    def increasePoints(self, transmitter, receiver):
        """
        incrementa los puntos de los user profiles tanto del usuario solicitante
        como del usuario receptor de la solicitud
        """
        transmitter.get_profile().add_points(5)
        receiver.get_profile().add_points(5)

    def save(self, user):
        """
            Crea la relacion de amigos y elimina la solicitud de amistad
            ademas incrementa en 5 el puntaje en el perfil de ambos usuarios
        """
        amigo = UserProfile.objects.get(user = self.cleaned_data['amigo'])
        amigo.amigos.add(user.get_profile())
        self.increasePoints(amigo.user,user)
        self.delete(user)
        return self

class InvitationForm(forms.Form):
    destinatario = forms.EmailField(label='Para',
                                    max_length=50,
                                    error_messages={'invalid': 'El correo no es válido o ha ingresado mas de uno.'},
                                    help_text="email@email.com")
    contenido = forms.CharField(max_length=120,
                                widget=forms.Textarea,
                                help_text="Invita a tu amigo con tus propias palabras")
    
    def send(self, user):
        """
        Envia la invitacion al correo destinatario
        """
        subject = 'Invitación al concurso "Yo estuve en Machu Picchu" '
        from_email, to = user.email, self.cleaned_data['destinatario']
        text_content = self.cleaned_data['contenido']
        context = Context({ 'text_content': text_content, 'user':user })
        t = loader.get_template('fotos/invitacion/template_invitacion.html')
        html_content = t.render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

class EnviarMensajeForm(InvitationForm):
    destinatario = forms.EmailField(max_length=50, widget = forms.HiddenInput())

    def send(self, user):
        """
        Envia el mensaje al correo asociado al perfil de usuario
        """
        subject = '"Yo estuve en Machu Picchu": %s te ha enviado un mensaje ' % user.first_name
        from_email, to = user.email, self.cleaned_data['destinatario']
        text_content = self.cleaned_data['contenido']
        context = Context({ 'text_content': text_content, 'user':user })
        t = loader.get_template('fotos/mensaje/template_mensaje.html')
        html_content = t.render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
class TemporadaAdminForm(forms.ModelForm):
    class Meta:
        model = Temporada
        exclude = ['max_fotos_per_user', 'ganadores_por_votos',]


    def clean(self):
        """
        Si esta editanto el objeto, verifica que no haya cambiado las fechas
        de inicio y fin
        si esta creando un nuevo objeto
        verifica que se hayan ingresado las fechas de inicio y fin
        verifica que la fecha inicio sea posterior a la fecha fin
        verifica que la fecha inicio ingresada sea posterior a cualquier fecha fin existente
        """
        if 'fecha_inicio' in self.cleaned_data and 'fecha_fin' in self.cleaned_data:
            if 'temporadaId' in self.data:
                temporada = get_object_or_404(Temporada, id=self.data['temporadaId'])
                if temporada.fecha_fin != self.cleaned_data['fecha_fin'] or temporada.fecha_inicio != self.cleaned_data['fecha_inicio']:
                    raise forms.ValidationError(u'No esta permitido cambiar las fechas de inicio y/o fin de temporada.')
                else:
                    return self.cleaned_data
            else:                
                very_last_temp = Temporada().get_very_last_temporada()
                if very_last_temp:
                    if very_last_temp.fecha_fin >= self.cleaned_data['fecha_inicio']:
                        raise forms.ValidationError(u"La fecha de inicio debe ser posterior a la fecha de finalización %s que corresponde a la última temporada creada." % str(very_last_temp.fecha_fin))
                if self.cleaned_data['fecha_inicio'] < self.cleaned_data['fecha_fin']:
                    return self.cleaned_data
                raise forms.ValidationError(u"La fecha de inicio debe ser anterior a la fecha de finalización.")
        raise forms.ValidationError(u"Las fechas de inicio y fin son obligatorias")
        
    def clean_titulo(self):
        """
        Verifica que el titulo sea unico, a menos que este editando el objeto
        """
        if Temporada.objects.filter(titulo=self.cleaned_data['titulo']):
            if 'temporadaId' in self.data:
                temporada = get_object_or_404(Temporada, id=self.data['temporadaId'])
                if temporada.titulo == self.cleaned_data['titulo']:
                    return self.cleaned_data['titulo']
            raise forms.ValidationError(u'Ya existe una temporada con este título')
        return self.cleaned_data['titulo']
            

    #def save(self):
    #    """
    #    Guarda los cambios realizados y lo el nuevo registro de temporada
    #    además, si es un nuevo registro le crea sus jobs de inicio y fin
    #    de temporada en en crontab
    #    """
    #    super(TemporadaAdminForm, self).save()
        #if 'temporadaId' in self.data:
        #    os.system('(sudo crontab -l; echo "07 13 12 4 2 sudo python /home/giussepi/demo/public_html/MP100/private/MP100/manage.py prueba") | sudo crontab -')
        
class GanadorFinalistaForm(forms.Form):
    """
    Formularios para elegir a un ganadores finalista entre los ganadores
    de las temporadas
    """
    selected = forms.BooleanField(required=False)
    foto_id = forms.IntegerField(widget = forms.HiddenInput())
    comentario = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={'class':'vLargeTextField'}),
        required=False,
        )
    winner = forms.BooleanField(required=False)

    def save(self):
        """
        Registra en la tabla GranGanador al finalista seleccinado entre
        los ganadores
        """
        foto = get_object_or_404(Foto, id=self.cleaned_data['foto_id'])
        try:
            g=GranGanador.objects.get(codigo_foto=foto)
            if not self.cleaned_data['selected']:
                g.delete()
            elif self.cleaned_data['comentario'] != g.comentario or \
                    self.cleaned_data['winner'] != g.winner:
                g.comentario=self.cleaned_data['comentario']
                g.winner=self.cleaned_data['winner']
                g.save()
        except ObjectDoesNotExist:
            if self.cleaned_data['selected']:                
                GranGanador.objects.create(
                    codigo_foto=foto, 
                    comentario=self.cleaned_data['comentario'],
                    winner=self.cleaned_data['winner'])

class PanoramicWinnerForm(forms.Form):
    """
    Formulario para elegir a un ganador panoramico
    """
    selected = forms.BooleanField(required=False)
    foto_id = forms.IntegerField(widget = forms.HiddenInput())
    comentario = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={'class':'vLargeTextField'}),
        required=False,
        )
    winner = forms.BooleanField(required=False)

    def save(self):
        """
        Registra en la tabla a la foto panorámica seleccinada
        """
        foto = get_object_or_404(Foto, id=self.cleaned_data['foto_id'])
        try:
            g=PanoramicWinner.objects.get(codigo_foto=foto)
            if not self.cleaned_data['selected']:
                g.delete()
            elif self.cleaned_data['comentario'] != g.comentario or \
                    self.cleaned_data['winner'] != g.winner:
                g.comentario=self.cleaned_data['comentario']
                g.winner=self.cleaned_data['winner']
                g.save()
        except ObjectDoesNotExist:
            if self.cleaned_data['selected']:                
                PanoramicWinner.objects.create(
                    codigo_foto=foto, 
                    comentario=self.cleaned_data['comentario'],
                    winner=self.cleaned_data['winner'])

###

class ProfessionalWinnerForm(forms.Form):
    """
    Formulario para elegir a un ganador professional
    """
    selected = forms.BooleanField(required=False)
    foto_id = forms.IntegerField(widget = forms.HiddenInput())
    comentario = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={'class':'vLargeTextField'}),
        required=False,
        )
    winner = forms.BooleanField(required=False)

    def save(self):
        """
        Registra en la tabla ProfessionalWinner a la foto profesional
        seleccinada
        """
        foto = get_object_or_404(Foto, id=self.cleaned_data['foto_id'])
        try:
            g=ProfessionalWinner.objects.get(codigo_foto=foto)
            if not self.cleaned_data['selected']:
                g.delete()
            elif self.cleaned_data['comentario'] != g.comentario or \
                    self.cleaned_data['winner'] != g.winner:
                g.comentario=self.cleaned_data['comentario']
                g.winner = self.cleaned_data['winner']
                g.save()
        except ObjectDoesNotExist:
            if self.cleaned_data['selected']:                
                ProfessionalWinner.objects.create(
                    codigo_foto=foto, 
                    comentario=self.cleaned_data['comentario'],
                    winner=self.cleaned_data['winner'])
