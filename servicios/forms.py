#-*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from common.validators import validate_name, validate_user
from django.core.files.images import get_image_dimensions
from portal.forms import HorizRadioRenderer
from servicios.models import TipoServicio, Servicio, Ubicacion, Foto, Opinion, \
    Caracteristica, Puntaje


class BusquedaForm(forms.Form):
    """
    Formulario para la búsqueda de servicios
    """
    ubicacion = forms.CharField(label=_(u"Looking for THE place"), required=False)
    viewport = forms.CharField(widget=forms.HiddenInput, required=False)
    location = forms.CharField(widget=forms.HiddenInput, required=False)
    nombre = forms.CharField(label=_(u"By name") ,required=False)
    tipo = forms.ModelChoiceField(queryset=TipoServicio.objects.all(),
                                  label=_(u"Type of service"),
                                  required=False)


class LoginForm(forms.Form):
    """
    Formulario para el login de los administradores de servicios
    """
    email = forms.EmailField(label=u"e-mail")
    contrasena = forms.CharField(widget=forms.PasswordInput,
                                 label=_(u"Password"))


class RecuperarForm(forms.Form):
    """
    Formulario para recuperar una contraseñá
    """
    email = forms.EmailField(label=u"e-mail")


class CambioForm(forms.Form):
    """
    Formlario para realizar el cambio de contraseña
    """
    old_pass = forms.CharField(widget=forms.PasswordInput,
                               label=_(u"Old password"))
    new_pass1 = forms.CharField(widget=forms.PasswordInput,
                                label=_(u"New password"))
    new_pass2 = forms.CharField(widget=forms.PasswordInput,
                                label=_(u"New password(repeat)"))


class ServicioPublicoForm(forms.ModelForm):
    """
    Formulario para el ingreso de un nuevo servicio por parte de cualquier
    usuario sin necesidad de ser administrador
    """
    class Meta:
        model = Servicio
        fields = ('nombre', 'tipo_servicio', 'foto_principal')

#    def save(self, commit=True):
#        servicio = super(ServicioPublicoForm, self).save(commit=False)
#        if self.cleaned_data["foto_principal"]:
#            servicio.foto_principal = self.cleaned_data['foto_principal']
#        else:
#            servicio.foto_principal = settings.MEDIA_URL + "servicios/fotos/no_image.jpg"
#            servicio.width = 44
#            servicio.height = 44
#        if commit:
#            servicio.save()
#        return servicio


class ServicioPrivadoForm(ServicioPublicoForm):
    """
    Formulario para el ingreso de un nuevo servicio por parte de un
    administrador que manejara el perfil
    """
    nombre = forms.CharField(label=_(u"Name of service"))
    email = forms.EmailField(label=_(u"e-mail"), validators=[validate_user])
    LANGUAGE_CHOICES = (
        (u"en", _(u"English")),
        (u"es", _(u"Spanish")),
    )
    idioma = forms.ChoiceField(label=_(u"Language"), choices=LANGUAGE_CHOICES,
                               initial=u"es")
    contrasenia = forms.CharField(label=_(u"Password"),
                                  widget=forms.PasswordInput)
    terminos = forms.BooleanField(label=_(u"I accept terms and conditions"))
    instance = forms.BooleanField(widget=forms.HiddenInput, required=False)

    class Meta(ServicioPublicoForm.Meta):
        pass


class ServicioEdicionForm(forms.ModelForm):
    """
    Formulario para la edición de un servicio por su administrador dentro
    del perfil privado
    """
    def __init__(self, *args, **kwargs):
        """
        Llena el widget de características según el tipo de servicio
        """
        super(ServicioEdicionForm, self).__init__(*args, **kwargs)
        if kwargs["instance"]:
            self.fields["caracteristicas"] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=Caracteristica.objects.filter(
                    tipo_servicio=kwargs["instance"].tipo_servicio
                )
            )

    class Meta:
        model = Servicio
        fields = ("nombre", "tipo_servicio", "website", "telefono",
                  "descripcion", "subtipo_servicio", "caracteristicas")


class ServicioPanoramicaForm(forms.ModelForm):
    """
    Formulario para subir o modificar una foto panorámica de un servicio
    """
    class Meta:
        model = Servicio
        fields = ("foto_panoramica",)

    def clean_foto_panoramica(self):
        """
        Verificación del tamaño mínimo de la foto
        """
        foto = self.cleaned_data.get("foto_panoramica")
        if not foto:
           raise forms.ValidationError(_("You must select a picture"))
        else:
           w, h = get_image_dimensions(foto)
           if w < 200:
               raise forms.ValidationError(_("It must be at least 975px width"))
           if h < 100:
               raise forms.ValidationError(_("It must be at least 376px height"))
        return foto


class UbicacionForm(forms.ModelForm):
    """
    Formulario para ubicar un punto dentro de un mapa
    """
    direccion = forms.CharField(label=_(u"Address"))
    latitud = forms.CharField(widget=forms.HiddenInput, required=False)
    longitud = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Ubicacion

    def clean(self):
        cleaned_data = self.cleaned_data
        latitud = cleaned_data.get("latitud")
        longitud = cleaned_data.get("longitud")

        if not latitud or not longitud:
            msg = _(u"Es necesario que coloque el marcador ubicando su posición en el mapa")
            self._errors["direccion"] = self.error_class([msg])

            del cleaned_data["latitud"]
            del cleaned_data["longitud"]

        return cleaned_data


class FotoForm(forms.ModelForm):
    """
    Formulario para subir o modificar una foto
    """
    principal = forms.BooleanField(label=_(u"Main photo"), required=False)

    class Meta:
        model = Foto
        fields = ("nombre", "imagen", "descripcion")


class EditFotoForm(FotoForm):
    """
    Formulario para subir o modificar una foto
    """
    id = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta(FotoForm.Meta):
        fields = ("id", "nombre", "descripcion")


class OpinionForm(forms.ModelForm):
    """
    Formulario para dejar una opinión
    """

    class Meta:
        model = Opinion
        fields = ("texto",)


class PuntajeForm(forms.ModelForm):
    """
    Formulario para dejar una puntuación
    """
    PUNTUACION_CHOICES = (
        (1, _(u"Poor")),
        (2, _(u"Fair")),
        (3, _(u"Good")),
        (4, _(u"Very good")),
        (5, _(u"Excellent")),
    )

    puntuacion = forms.ChoiceField(widget=forms.Select,
                                   choices=PUNTUACION_CHOICES,
                                   label=_(u"Score"),
                                   initial=5)

    class Meta:
        model = Puntaje
        fields = ("puntuacion",)


class ContactoForm(forms.Form):
    """
    Formulario de contacto con un administrador de servicio
    """
    nombre = forms.CharField(label=_("name"), validators=[validate_name])
    email = forms.EmailField(label=u"e-mail")
    mensaje = forms.CharField(label=_("message"), widget=forms.Textarea)
