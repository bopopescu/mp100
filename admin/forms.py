#-*- coding: utf-8 -*-

from django import forms
from django.shortcuts import get_object_or_404
from MP100.fotos.models import Foto, Temporada

class FavoritaForm(forms.Form):
    """
    Formulario para escoger un numero de fotos mas votadas
    """
    numero = forms.CharField(label=u"Número de favoritas")


class HabilitarFotosForm(forms.Form):
    """
    Formulario para habilitar todas las fotos para cualquier
    temporada
    """
    habilitar = forms.BooleanField()
    
    def save(self):
        """
        Habilita todas las fotos
        """
        Foto.objects.all().update(temporada_habilitado = 'S')


class SendEmailForm(forms.Form):
    """
    Formulario para el envío de e-mails por parte del admin
    """
    para = forms.CharField()
    texto = forms.CharField(widget=forms.Textarea,
                            help_text=u"Separe los correos con comas")

class VerifyVotosForm(forms.Form):
    """
    Formulario para el filtro de votos
    """
    pattern = forms.CharField()

class DesqualifyUserForm(forms.Form):
    """
    Formulario para descalificar un usuario
    """
    foto_id = forms.IntegerField()
    
    def save(self):
        """
        Descalifica al usuario dueño de la foto con id=foto_id
        """
        f = get_object_or_404(Foto, id=self.cleaned_data['foto_id'])
        f.codigo_user.get_profile().delete_user()


