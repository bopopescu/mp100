from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.views import login, logout, logout_then_login
from django.contrib import admin
from django.contrib.sites.models import Site
#from MP100.admin.views import manage_db
from MP100.portal.forms import RegisterForm
from MP100 import captcha
from sitemap import FotoSitemap, UserProfileSitemap, ComentarioSitemap
from zinnia.sitemaps import TagSitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import AuthorSitemap

from os.path import dirname
basedir = dirname(__file__)
media = '%s/public/media/' % basedir
ZINNIA_MEDIA_URL = '%s/public/media/zinnia/' % basedir
admin.autodiscover()

handler404 = 'MP100.portal.views.index'

sitemaps = {
    'Foto': FotoSitemap,
    'UserProfile': UserProfileSitemap,
    'Comentario': ComentarioSitemap,
    'tags': TagSitemap,
    'blog': EntrySitemap,
    'authors': AuthorSitemap,
    'categories': CategorySitemap,    
}

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('MP100',),
}
form_register = RegisterForm();
html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
domain = Site.objects.get_current().domain
urlpatterns = patterns('',
     (r'^', include('MP100.portal.urls')),
     (r'^user/', include('MP100.fotos.urls')),
     (r'^usuario/', include('MP100.usuario.urls')),
     (r'^bb/', include('djangobb.urls')),
     #(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
     (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
     (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
     (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
     (r'^admin/', include('MP100.admin.urls')),
     (r'^admin/', include(admin.site.urls)),
     (r'^blog/', include('zinnia.urls')),
     (r'^servicios/', include('servicios.urls')),
     # (r'^blog/', include('zinnia.urls'),
     #  {'extra_context':{'form_register': form_register,
     #                    'html_captcha':html_captcha,
     #                    'domain':domain}}),
     #(r'^blog/', include('zinnia.urls')),
     (r'^comments/', include('django.contrib.comments.urls')),
     # media url
    (r'^tinymce/', include('tinymce.urls')),
    (r'^media/(?P<path>.*)$','django.views.static.serve',
        {'document_root': media,'show_indexes': True}),
    (r'^media/zinnia/(?P<path>.*)$','django.views.static.serve',
        {'document_root': ZINNIA_MEDIA_URL,'show_indexes': True}),
)



#urlpatterns += patterns('django.contrib.auth.views',		
#       url(r'^$', 'login', {'template_name': 'registration/login.html', 'SSL': settings.ENABLE_SSL }, name='login'),
#       url(r'^accounts/login/$', 'login', {'template_name': 'registration/login.html', 'SSL': settings.ENABLE_SSL }, name='login'),
#       url(r'^logout/$', logout_then_login, {'SSL': settings.ENABLE_SSL }, name='logout'),
#)
