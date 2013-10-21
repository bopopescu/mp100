from django.contrib.sitemaps import Sitemap
from fotos.models import Foto, UserProfile, Comentario

class FotoSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        return Foto.objects.all()
    
    def lastmod(self, obj):
        return obj.fecha

class UserProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    
    def items(self):
        return UserProfile.objects.all()
    
class ComentarioSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8
    
    def items(self):
        return Comentario.objects.all()
    
    def lastmod(self, obj):
        return obj.fecha
    
#class NoticiaSitemap(Sitemap):
#    changefreq = "daily"
#    priority = 0.9
#    
#    def items(self):
#        return Noticia.objects.all()
#    
#    def lastmod(self, obj):
#        return obj.fecha