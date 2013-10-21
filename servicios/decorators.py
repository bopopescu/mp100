#-*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from servicios.forms import CambioForm


def change_password(view):
    """
    Decorador para cambiar la contraseña en alguna vista de administrador
    de servicios
    """
    def _dec(request, *args, **kwargs):
        form = CambioForm()
        if request.method == "POST":
            if "cambio" in request.POST:
                form = CambioForm(request.POST)
                if form.is_valid():
                    user = authenticate(username=request.user.username,
                                        password=form.cleaned_data['old_pass'])
                    if user is not None:
                        if form.cleaned_data['new_pass1'] == form.cleaned_data['new_pass2']:
                            user.set_password(form.cleaned_data['new_pass1'])
                            user.save()
                        else:
                            form.errors["new_pass1"] = [_(u"New passwords don't match")]
                    else:
                        form.errors["old_pass"] = [_(u"Old password is incorrect")]
        kwargs["cambio_form"] = form
        return view(request, *args, **kwargs)
    return _dec