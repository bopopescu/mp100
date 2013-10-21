#from django.utils.feedgenerator import Rss201rev2Feed
#from django.contrib.sites.models import Site
#from django.contrib.syndication.views import Feed
#from django.core.urlresolvers import reverse
#from MP100.fotos.models import Noticia
#
#current_site = Site.objects.get_current()
#
#class UltimasNoticiasFeed(Feed):
#    title = "YoestuveenMachuPicchu.com site news"
#    link = "/feeds/" 
#    description = "Updates on changes and additions to YoestuveenMachuPicchu.com."
#    feed_type = Rss201rev2Feed
#
#    #ya estan creados los templates x si se les kiere dar estilo    
#    #title_template = 'feeds/noticias_title.html'
#    #description_template = 'feeds/noticias_descripcion.html'
#    
#    
#    def items(self):
#        return Noticia.objects.order_by('-fecha')[:10]
#    
#    def last_2_items(self):
#        return Noticia.objects.order_by('-fecha')[:2]    
#        
#    def last_3_items(elf):
#        return Noticia.objects.order_by('-fecha')[:3]    
#        
#    def item_title(self, item):
#        return item.titulo
#
#    def item_description(self, item):
#        return item.descripcion
#       
#    def item_link(self, item):
#        return reverse('portal_noticia_detail', args=[item.id,] )
#    