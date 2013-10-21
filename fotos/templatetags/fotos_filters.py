#-*- coding: utf-8 -*-

from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

import re

register = template.Library()

@register.filter()
@stringfilter
def youtube(url, autoescape = None):
    regex = re.compile(r"^(http://)?(www\.)?(youtube\.com/watch\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})")
    match = regex.match(url)
    if not match: return ""
    video_id = match.group('id')
    return mark_safe("""
    <iframe title="YouTube video player" class="youtube-player" type="text/html" width="475px" height="360" src="http://www.youtube.com/embed/%s" frameborder="0" allowFullScreen>
        <p>Tu explorador de internet no soporta iframes, mira el video <a href="%s"> aqui </a> </p>
    </iframe>
    """
    % (video_id, url))
youtube.needs_autoescape = True # Don't escape HTML
