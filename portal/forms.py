# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.forms.widgets import RadioSelect
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.core.files.images import get_image_dimensions
from django.contrib.formtools.wizard import FormWizard
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from MP100.fotos.models import UserProfile, Foto, Categoria, Denuncia, Temporada, Estadistica
from MP100.countries.models import Country
from MP100.common.models import Departamento

class SignupForm(forms.Form):
    email = forms.EmailField(label=_(u'Aleas'))    
    password = forms.CharField(label=_(u'Contraseña'), max_length=30,
                               widget=forms.PasswordInput(render_value=False))

    def clean(self):
        email = self.cleaned_data.get('email', None)
        password = self.cleaned_data.get('password', None)
        if not email or not password:
            forms.ValidationError(_(u"Ingrese su email y contraseña."))
        try:
            user = User.objects.get(email=email)
        except:
            raise forms.ValidationError(_(u"Email o contraseña incorrectos."))
        from django.contrib.auth import authenticate
        self.user_cache = authenticate(username=user.username, 
                                       password=password)
        if self.user_cache is None:
            raise forms.ValidationError(_(u"Email o contraseña incorrectos."))
        elif not self.user_cache.is_active:
            raise forms.ValidationError(_(u"Su cuenta esta desactivada."))
        return self.cleaned_data

    def save(self, request):
        from django.contrib.auth import login
        login(request, self.user_cache)
        
    def set_data(self, email, password):
        self.data = self.data.copy()
        self.data['email'] = email
        self.data['password'] = password
        return self

class SubirFotoForm(ModelForm):    
    codigo_user = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(),
                                       widget=RadioSelect())
    
    class Meta:
        model = Foto
        #exclude = ['fans', 'vistas', 'escogida', 'codigo_user', 'uploaded_photos']
        exclude = ['vistas', 'escogida', 'codigo_user', 'uploaded_photos']

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [ 'codigo_user','foto', 'titulo', 'categoria', 'descripcion', 'ediciones']

    def save(self):
        """
            crea un nuevo registro de foto al respectivo usuario
            incrementa el nro de fotos subidas por el usuario
            incrementa el numero de fotos subidas en la tabla Estadistica
        """
        user = User.objects.get(id=self.cleaned_data['codigo_user'])
        user.fotos.create(foto=self.cleaned_data['foto'],
                          titulo=self.cleaned_data['titulo'],
                          categoria=self.cleaned_data['categoria'],
                          descripcion=self.cleaned_data['descripcion'],
                          ediciones=self.cleaned_data['ediciones'],)
        user.get_profile().increase_uploaded_photos()
        Estadistica.objects.get_or_create(id=1)[0].add_foto()
        return self

    def clean_descripcion(self):
        if 'descripcion' in self.cleaned_data:
            if self.cleaned_data['descripcion'] == _(u'Description to be published with your photo.'):
                return ''
        return self.cleaned_data['descripcion']

    def clean_ediciones(self):
        if 'ediciones' in self.cleaned_data:
            if self.cleaned_data['ediciones'] == _(u'Please describe any minors edits or retouching including use of HRD. This information is for judges user and will not be plublished with your photo.'):
                return ''
        return self.cleaned_data['ediciones']
                   
    def is_valid(self):
        """
            Redefine es is_valid() y aumenta la validacion del tamanio
            de la imagen
        """
        result = super(self.__class__, self).is_valid()
        if result:
            (width,height) = get_image_dimensions(self.cleaned_data['foto'])
            #if not (width >= 1600 or height >= 1600):
            #if not (width >= 960 or height >= 960):            
            #    return (False, _(u'Your photo must measure at least 960 pixels in length or width.'))
        return (result, '')

class SearchForm(forms.Form):
    texto = forms.CharField(label=_(u'por nombre'), max_length=50, required = False)
    
class SearchFilterForm(SearchForm):
    pais = forms.ModelChoiceField(label=_(u'por país'), queryset=Country.objects.all(),
                                  empty_label="---------", required = False)
    
    def get_ordered_list(self, user_list, usuarios_per_line=4):
        """Ordena la lista 'user_list' en una lista de N listas
        con un numero de elementos igual o menor al valor de la variable
        'usuarios_per_line'"""
        lista_usuarios = []
        nro_elementos = usuarios_per_line
        nro_filas = -1
        for usuario in user_list:
            if nro_elementos == usuarios_per_line:
                lista_usuarios.append([])
                nro_filas = nro_filas + 1
            if nro_elementos > 0:
                lista_usuarios[nro_filas].append(usuario)
                nro_elementos = nro_elementos -1
            if nro_elementos == 0:
                nro_elementos = usuarios_per_line
        return lista_usuarios
        
    def apply_filters(self, user_list):
        """Aplica a user_list(que es un QuerySet) el filtrado por pais y nombre
        de usuario"""
        if self.cleaned_data['texto'] and self.cleaned_data['pais']:
            return user_list.filter(Q(userprofile__pais = self.cleaned_data['pais']) & (Q(username = self.cleaned_data['texto']) | Q(first_name = self.cleaned_data['texto']) | Q(last_name = self.cleaned_data['texto'])))
        if self.cleaned_data['texto']:
            return user_list.filter(Q(username = self.cleaned_data['texto']) | Q(first_name = self.cleaned_data['texto']) | Q(last_name = self.cleaned_data['texto']))
        if self.cleaned_data['pais']:
            return user_list.filter(userprofile__pais = self.cleaned_data['pais'])
        return user_list
    
    def paginate_list(self, request, lista_usuarios, items_per_page=8):
        """ divide la lista_usuarios en varias paginas de 8 elementos cada una """
        paginator = Paginator(lista_usuarios, items_per_page)
        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
    
        # If page request (9999) is out of range, deliver last page of results.
        try:
            contacts = paginator.page(page)
        except (EmptyPage, InvalidPage):
            contacts = paginator.page(paginator.num_pages)
        return contacts
        #return render_to_response('list.html', {"contacts": contacts})

class TerminosCondicionesForm(forms.Form):
    accepted = forms.BooleanField(label=_(u'Acepto'), error_messages={'required': _(u'Debe aceptar los términos y condiciones para continuar con el registro.') })
    
    def clean_accepted(self):
        """
            Verifica que se haya aceptado los términos y condiciones.
        """
        if 'accepted' in self.cleaned_data:
            if self.cleaned_data['accepted']:
                return self.cleaned_data['accepted']
        raise template.TemplateSyntaxError(_(u'No ha aceptado los términos y condiciones.'))

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))    
    
class RegisterForm(ModelForm):
    
    fecha_nacimiento = forms.DateField(input_formats=('%d-%m-%Y',),
                                       widget=forms.DateInput(attrs={'class':'textbox special_gray calendar clearInput no_bottom_margin',
                                                                     'title':_(u'Date of Birth'), 'value':_(u'Date of Birth')}))
    username = forms.CharField(max_length=30, label = _(u'Aleas'),
                                widget=forms.TextInput(attrs={'class':'textbox special_gray clearInput',
                                                              'title':_(u'Screen Name'), 'value':_(u'Screen Name')}))
                               
    password1 = forms.CharField(max_length=30,
                                label=_(u'Contraseña'),
                                widget=forms.PasswordInput(render_value=False,
                                                           attrs={'class':'textbox special_gray', 'style':'display:none;'}), )
    password2 = forms.CharField(max_length=30,
                                label=_(u'Confirmar contraseña'),
                                widget=forms.PasswordInput(render_value=False,
                                                           attrs={'class':'textbox special_gray', 'style':'display:none;'}),)
    nombres = forms.CharField(max_length=50, label=_(u'Nombres'), widget=forms.TextInput(attrs={'class':'textbox special_gray clearInput',
                                                                                                'title':_(u'First Name'), 'value':_(u'First Name')}))
    apellidos = forms.CharField(max_length=50, label=_(u'Apellidos'), widget=forms.TextInput(attrs={'class':'textbox special_gray clearInput',
                                                                                                'title':_(u'Last Name'), 'value':_(u'Last Name')}))
    
    FEMENINO_ = u'F'
    MASCULINO_ = u'M'
    tipo_sexo=((FEMENINO_,_(u'Female')),
                (MASCULINO_,_(u'Male')),)
    
    tipo_titulo = ( 
        (u'Mr.', "Mr"),
        (u'Mrs.', "Mrs"),
        (u'Ms.', "Ms"),
        (u'Miss.',"Miss"),
        (u'Dr.',"Dr"),        
    )    
    titulo = forms.ChoiceField(choices=tipo_titulo,label=_(u'Título'))
    sexo = forms.ChoiceField(choices=tipo_sexo, widget=forms.RadioSelect(renderer=HorizRadioRenderer), label=_(u'Sexo'))
    correo = forms.EmailField(label=_(u'Correo'),
                                widget=forms.TextInput(attrs={'class':'textbox special_gray clearInput',
                                                              'title':_(u'Email'), 'value':_(u'Email')}))
                              
    foto = forms.ImageField(required=False,
                            widget=forms.FileInput(attrs={'class':'textbox special_gray'}))
    pais = forms.ModelChoiceField(queryset=Country.objects.all(),
                                  empty_label=u'Country Residence',
                                  label=_(u'País'),
                                  widget=forms.Select(attrs={'class':'textbox special_gray no_bottom_margin'})
                                  ,)

    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(),
                                  empty_label=u'Department (Peru only)',
                                  label=_(u'Departamento (sólo Perú)'),
                                  required=False,
                                  widget=forms.Select(attrs={'class':'textbox special_gray no_bottom_margin'})
                                  ,)
    LANGUAGE_CHOICES = (
        (u"en", _(u"English")),
        (u"es", _(u"Spanish"))
    )
    idioma = forms.ChoiceField(choices=LANGUAGE_CHOICES, label=_(u'Language'),
                               widget=forms.RadioSelect(renderer=HorizRadioRenderer))    
    accept_conditions = forms.BooleanField(error_messages={'required': _(u'It is mandatory to accept the Contest Terms & Conditions')})
    accept_email_updates = forms.BooleanField(required = False,
                                              widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    accept_sponsors_emails = forms.BooleanField(required = False,
                                                widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    class Meta:
        model = UserProfile
        exclude = ['user', 'height', 'width', 'me_gusta_temp',]
    
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'The passwords did not match'))
        else:
            raise forms.ValidationError(_(u'This field is required'))
        return self.cleaned_data
    
    def clean_nombres(self):
        if self.cleaned_data['nombres']:
            if self.cleaned_data['nombres'] == _(u'First Name'):
                raise forms.ValidationError(_(u'This field is required'))
        return self.cleaned_data['nombres']

    def clean_apellidos(self):
        if self.cleaned_data['apellidos']:
            if self.cleaned_data['apellidos'] == _(u'Last Name'):
                raise forms.ValidationError(_(u'This field is required'))
        return self.cleaned_data['apellidos']    
    
    def clean_username(self):
        if self.cleaned_data['username']:
            if self.cleaned_data['username'] == _(u'Screen Name'):
                raise forms.ValidationError(_(u'This field is required'))
            if User.objects.filter(username = self.cleaned_data['username']):
                raise forms.ValidationError(_(u'This Screen Name is already registered'))
        return self.cleaned_data['username']
    
    def clean_correo(self):
        if self.cleaned_data['correo']:
            if User.objects.filter(email = self.cleaned_data['correo']):
                raise forms.ValidationError(_(u'This email is already registered'))
        return self.cleaned_data['correo']

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
                    #return (False, 'La imagen debe ser como máximo de 1024 x 768')
                #restriccion de tamanio minimo
                #if (width * height < 2000000):
                #    return (False, 'La imagen debe tener como mínimo 2 Mega Pixeles')
                #restriccion de tamanio maximo
                #pendiente
                #restriccion de peso
                #pendiente
        return (result, '')
            
    def save(self):
        """
            Crea un nuevo usuario y su perfil y guarda todos los datos ingresados 
        """
        new_user = User.objects.create_user(username=self.cleaned_data['username'],
                                            email=self.cleaned_data['correo'],
                                            password=self.cleaned_data['password1'],)        
        new_user.first_name=self.cleaned_data['nombres']
        new_user.last_name=self.cleaned_data['apellidos']
        new_user.is_staff=False
        new_user.is_active=False
        new_user.is_superuser=False
        new_user.last_login=datetime.now()
        new_user.date_joined=datetime.now()
        new_user.save()
        new_profile=new_user.get_profile()
        new_profile.pais = self.cleaned_data['pais']
        new_profile.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        new_profile.titulo = self.cleaned_data['titulo']
        new_profile.sexo = self.cleaned_data['sexo']
        new_profile.idioma = self.cleaned_data['idioma']
        if self.cleaned_data['departamento'] and (self.cleaned_data['pais'].printable_name == 'Peru'):
            new_profile.departamento = self.cleaned_data['departamento']
        if self.cleaned_data['foto']:
            new_profile.foto = self.cleaned_data['foto']
        else:    
            new_profile.foto = settings.USERPROFILE_PHOTO_PATH+"no_image.jpg"
            new_profile.width = 113
            new_profile.height = 118
        if self.cleaned_data['accept_email_updates']:
            new_profile.accept_email_updates = self.cleaned_data['accept_email_updates']
        if self.cleaned_data['accept_sponsors_emails']:
            new_profile.accept_sponsors_emails = self.cleaned_data['accept_sponsors_emails']
        new_profile.save()    
        return new_user        

class CompleteRegisterForm(FormWizard):
    def done(self, request, form_list):
        self.save(form_list[1].cleaned_data) 
        return HttpResponseRedirect(reverse('registrado'))    
    
    def save(self, cleaned_data):        
        new_user = User.objects.create_user(username=cleaned_data['username'],
                                            email=cleaned_data['correo'],
                                            password=cleaned_data['password1'],)        
        new_user.first_name=cleaned_data['nombres']
        new_user.last_name=cleaned_data['apellidos']
        new_user.is_staff=False
        new_user.is_active=True
        new_user.is_superuser=False
        new_user.last_login=datetime.now()
        new_user.date_joined=datetime.now()
        new_user.save()
        new_profile=new_user.get_profile()
        new_profile.pais = cleaned_data['pais']
        new_profile.save()
        return new_user    
        
    def get_template(self, step):
        return u'portal/register/register.html'
    
class ReportConcernForm(forms.Form):
    TIPO_RAZONES = ((u'1',_(u'This image contains obscene or offensive content.')),
                    (u'2',_(u'This photo was not taken in or en route to the sanctuary of Machu Picchu.')),
                    (u'3',_(u'This photo was not taken by the user who submitted it or the user does not have rights to this photo.')),
                    (u'4',_(u'The image has been modified (for example, objects and/or people who were not present have been added) or edits not permitted were made (for example, drastic changes in the saturation and the exposure or use of digital filters).')),
                    (u'5',_(u'This photo was miscategorized (for example, a photograph without a person was placed in the category "People").'))
                    )    
    codigo_foto = forms.IntegerField(widget=forms.HiddenInput())
    codigo_user = forms.IntegerField(widget=forms.HiddenInput())
    codigo_temporada = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    razon = forms.ChoiceField(widget=RadioSelect(attrs={'class':'styled special_gray'}),
                              choices=TIPO_RAZONES,
                              required=False)
    comentario = forms.CharField(max_length=250,
                                 widget=forms.Textarea(attrs={'class': 'textarea_enter2 textbox special_gray countable1'}),
                                 required=False)
        
    def clean(self):
        if not self.cleaned_data['razon'] and not self.cleaned_data['comentario']:
            raise forms.ValidationError(_(u'You have to choose a concern or write down information about the concern'))
        return self.cleaned_data
        
    def save(self):
        """
        """
        new_denuncia = Denuncia(codigo_foto = get_object_or_404(Foto, id=self.cleaned_data['codigo_foto']),
                                codigo_user = get_object_or_404(User, id=self.cleaned_data['codigo_user'],))
        if self.cleaned_data['codigo_temporada']:
            new_denuncia.codigo_temporada = get_object_or_404(Temporada, id=self.cleaned_data['codigo_temporada'])
        if self.cleaned_data['razon']:
            new_denuncia.razon = self.cleaned_data['razon']
        if self.cleaned_data['comentario']:
            new_denuncia.comentario = self.cleaned_data['comentario']
        new_denuncia.save()
