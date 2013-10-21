#-*- coding: utf-8 -*-

from MP100.common.utils import direct_response
from django.shortcuts import redirect, reverse


def custom404(request):
    """
    Redirecciona los errores 404 a la página de inicio
    """
    return redirect(reverse('main_portal'))
