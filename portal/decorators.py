try:
    import json
except:
    import simplejson as json

from django.http import HttpResponse
from MP100.portal.models import Redes_Sociales
from forms import RegisterForm, SignupForm
from django.conf import settings
from MP100 import captcha
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from base64 import urlsafe_b64encode
from MP100.common.utils import sendHtmlMail


redes_sociales = Redes_Sociales.objects.all()
url_redes_sociales = {}
url_redes_sociales['Facebook'] = redes_sociales.get(nombre='Facebook').url
url_redes_sociales['Twitter'] = redes_sociales.get(nombre='Twitter').url
url_redes_sociales['Flickr'] = redes_sociales.get(nombre='Flickr').url

form_register = RegisterForm();
# codigo captcha
html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)


# def append_custom_context(func):
#     def wrapper(request, *args, **kwargs):
#         dictionary=	{'domain': request.META['HTTP_HOST'],
#                          'url_redes_sociales': url_redes_sociales,
#                          'form_register': form_register,
#                          'html_captcha': html_captcha}
#         if request.GET:
#             if 'form_login' in request.GET:
#                 dictionary['form_login']=request.GET['form_login']
#             if 'error' in request.GET:
#                 dictionary['error']= request.GET['error']
#             if 'datos_incorrectos' in request.GET:
#                 dictionary['datos_incorrectos'] =\
#                                                 request.GET['datos_incorrectos']
#             if 'new_pass_sended' in request.GET:
#                 dictionary['new_pass_sended'] = request.GET['new_pass_sended']
#         kwargs.update(dict(extra_context=dictionary))
#         return func(request, *args, **kwargs)
#     return wrapper

def get_ajax_login_form(request):
    response = "FAIL"
    extra_context = {'domain': request.META['HTTP_HOST'],
                     'url_redes_sociales': url_redes_sociales,
                     'form_register': form_register,
                     'html_captcha': html_captcha}
    if request.method == 'GET':
        form = SignupForm()
        extra_context['form'] = form
        return render_to_response(
            'portal/ajax/login.html',
            extra_context, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save(request)
            response = "OK"
    extra_context['form'] = form
    
    html = render_to_string(
        'portal/ajax/login.html',
        extra_context, context_instance=RequestContext(request))
    json_response = json.dumps({'response': response, 'html': html})
    return HttpResponse(json_response)


def get_ajax_register_form(request):
    captcha_error = u""
    response = "FAIL"
    extra_context = {'domain': request.META['HTTP_HOST'],
                     'url_redes_sociales': url_redes_sociales,
                     'html_captcha': html_captcha,
                     'MEDIA_URL': settings.MEDIA_URL}
    form = RegisterForm()
    if request.method == 'POST':
        check_captcha = captcha.submit(
            request.POST['recaptcha_challenge_field'],
            request.POST['recaptcha_response_field'],
            settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            # Captcha is wrong show a error ...
            captcha_error = _(u"Written words are incorrect")

        form = RegisterForm(request.POST, request.FILES)
	result = form.is_valid()
        
        if result[0] and not captcha_error:
            from django.contrib.auth import login, authenticate
	    successful_register=True
            user = form.save()
	    user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
	    #login(request, user)
            data = {'user_firstname': user.first_name,
		    'email': user.email,
		    'password': form.cleaned_data['password1'],
		    'mydomain': request.META['HTTP_HOST'],
		    'encryptedUsername': urlsafe_b64encode(str(user.id)),
                    'encryptedEmail': urlsafe_b64encode(str(user.email))}
	    if user.get_profile().idioma == u'es':
		subject = u'Machu Picchu 100 - Gracias por Registrarte!'
		template = "a-photo-registering_es.html"
	    else:
		subject = u"Machu Picchu 100 - Thank you for Registering!"
		template = "a-photo-registering_en.html"
            sendHtmlMail("info@machu-picchu100.com", subject,
                         template,
			 data, user.email)
            extra_context['captcha_error'] = captcha_error
	    extra_context['form'] = form
	    extra_context['successful_register'] = True
            #return render_to_response(
            #    'portal/ajax/post.html',
	    return render_to_response(
		'portal/ajax/register.html',
                extra_context, context_instance=RequestContext(request))

    extra_context['captcha_error'] = captcha_error
    extra_context['form'] = form
    return render_to_response(
        'portal/ajax/register.html',
        extra_context, context_instance=RequestContext(request))
