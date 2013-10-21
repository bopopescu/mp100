# -*- coding: utf-8 -*-
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth import login        
from django.conf import settings
from django.core.urlresolvers import reverse
from MP100.fotos import models
from datetime import datetime, timedelta        
import random

class BaseOperations(TestCase):
    def _create_user(self, username):
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username=username, 
                                                   email=username+'@user.com',
                                                   is_active=True)
        user.set_password('123')
        user.save()
        return user
    
    def _get_random_string(self, length):
        import string
        return ''.join(random.choice(string.letters) for i in xrange(length))

    def _create_foto(self, estado='M'):
        """
        crea una usuario, una categoria y una foto
        """
        uname = self._get_random_string(20)
        user = self._create_user(uname)
        categoria, created = models.Categoria.objects.get_or_create(
            nombre='nombre1',
            nombre_espaniol='nombre_espaniol',
            descripcion='descripcion',
            descripcion_espaniol='descripcion_espaniol')
        #print "creating foto for user %s" % uname 
        models.Foto.objects.create(estado=estado,
                                   temporada_habilitado='S',
                                   codigo_user=user,
                                   categoria=categoria,
                                   titulo='titulo',
                                   foto='images/social/Twitter.png',
                                   )
        profile = user.get_profile()
        profile.uploaded_photos=1
        profile.save()        

    def _create_foto_for(self, user):
        """
        crea una foto al usuario user, también le crea una categoría a la foto
        """
        categoria, created = models.Categoria.objects.get_or_create(
            nombre=self._get_random_string(5),
            nombre_espaniol=self._get_random_string(5),
            descripcion=self._get_random_string(5),
            descripcion_espaniol=self._get_random_string(5))
        #print "creating foto for user %s" % uname 
        models.Foto.objects.create(estado=u'M',
                                   temporada_habilitado='S',
                                   codigo_user=user,
                                   categoria=categoria,
                                   titulo='titulo',
                                   foto='images/social/Twitter.png',
                                   )
        profile = user.get_profile()
        profile.uploaded_photos+=1
        profile.save()        

    def _create_voto(self, user, foto, temporada):
        """
        Crea un voto del user 'user' para foto 'foto', en la 
        temporada 'temporada'. Además aumenta el número de votos realizados
        """
        models.Voto.objects.create(codigo_user=user,
                                   codigo_foto=foto,
                                   codigo_temporada=temporada)
        user.get_profile().nuevo_voto()

class WeeklyTopAmbassadors(BaseOperations):
    def test_WTA(self):
        """
        verifica que la funcion weekly_top_ambassadors agregue solo a como}
        máximo a 10 mbajadores cada vez que es ejecutada
        """
        #revisa que la funcion weekly_top_ambassadors funcione correctamente 
        #cuando no hay usuarios registrados
        models.weekly_top_ambassadors()
        self.assertEqual(models.TopAmbassador.objects.count(),0)
        #crea 7 usuarios
        for i in xrange(7):
            self._create_user(self._get_random_string(5))
        #revisa que la funcion weekly_top_ambassadors funcione correctamente
        #cuando hay menos de 10 usuarios registrado
        models.weekly_top_ambassadors()
        self.assertEqual(models.TopAmbassador.objects.count(),7)    
        #crea 13 usuarios
        for i in xrange(13):
            self._create_user(self._get_random_string(5))
        #revisa que la funcion weekly_top_ambassadors funcione correctamente 
        #cuando hay más de 10 usuarios tienen el mismo puntaje
        models.weekly_top_ambassadors()
        self.assertEqual(models.TopAmbassador.objects.count(),17)    
        #revisa que la funcion weekly_top_ambassadors funcione correctamente
        #en un caso con distintos puntajes
        for u in models.UserProfile.objects.all():
            u.add_points(random.randint(1,10000))
        models.weekly_top_ambassadors()
        self.assertEqual(models.TopAmbassador.objects.count(),27)    
        


class TopAmbassadorTest(BaseOperations):
    def test_get_last_top10(self):
        """
        verifica que la funcion get_last_top10 siempre retorne una lista de los 
        ultimos 10 ganadores
        """
        #revisa que funcione bien cuando la tabla TopAmbassador esta vacía
        top10 = models.TopAmbassador().get_last_top_10()
        self.assertEqual(top10, [])
        #crea 20 usuarios
        for i in xrange(20):
            self._create_user(self._get_random_string(5))
        #establece los 10 embajadores más votados
        models.weekly_top_ambassadors()
        #verifica que retorne a los últimos embajadores escojidos
        top10 = models.TopAmbassador().get_last_top_10()
        lastDate=models.TopAmbassador.objects.order_by("-fecha")[0].fecha
        self.assertEqual(lastDate,top10[0].fecha)
        #establece puntuaciones aleatorias a los 20 usuarios
        for u in models.UserProfile.objects.all():
            u.add_points(random.randint(1,10000))
        #establece los 10 embajadores más votados
        models.weekly_top_ambassadors()
        #verifica que retorne a los últimos embajadores escojidos
        top10 = models.TopAmbassador().get_last_top_10()
        lastDate=models.TopAmbassador.objects.order_by("-fecha")[0].fecha
        self.assertEqual(lastDate,top10[0].fecha)        
        

class badgesSystemTest(BaseOperations):
    # def setUp(self):
    #     #borra todas las temporadas
    #     models.Temporada.objects.all().delete()
    #     self.assertEquals(models.Temporada.objects.all(),"")

    #     #borra todas las fotos
    #     models.Fotos.objects.all().delete()
    #     self.assertEquals(models.Fotos.objects.all(),"")

    def test_levels_system(self):
        """
        verifica que los niveles alcanzado por los puntajes sean correctos
        """
        #crea un usuario
        user = self._create_user(self._get_random_string(5))
        
        #verifica los niveles alcanzados segun el puntaje
        #level 1: 0-1000
        p=user.get_profile()
        self.assertEquals(p.points,0)
        self.assertEquals(p.get_level(),1)
        p.add_points(1)
        self.assertEquals(p.get_level(),1)
        p.add_points(999)
        self.assertEquals(p.points,1000)
        self.assertEquals(p.get_level(),1)
        #level 2: 1001-2000
        p.add_points(1)
        self.assertEquals(p.points,1001)
        self.assertEquals(p.get_level(),2)
        p.add_points(999)
        self.assertEquals(p.points,2000)
        self.assertEquals(p.get_level(),2)
        #level 3: 2001-3000
        p.add_points(1)
        self.assertEquals(p.points,2001)
        self.assertEquals(p.get_level(),3)
        p.add_points(999)
        self.assertEquals(p.points,3000)
        self.assertEquals(p.get_level(),3)
        #level 4: 3001-4000
        p.add_points(1)
        self.assertEquals(p.points,3001)
        self.assertEquals(p.get_level(),4)
        p.add_points(999)
        self.assertEquals(p.points,4000)
        self.assertEquals(p.get_level(),4)
        #level 5: 4001-5000
        p.add_points(1)
        self.assertEquals(p.points,4001)
        self.assertEquals(p.get_level(),5)
        p.add_points(999)
        self.assertEquals(p.points,5000)
        self.assertEquals(p.get_level(),5)
        #level 6: 5001-6000
        p.add_points(1)
        self.assertEquals(p.points,5001)
        self.assertEquals(p.get_level(),6)
        p.add_points(999)
        self.assertEquals(p.points,6000)
        self.assertEquals(p.get_level(),6)
        #level 7: 6001-7000
        p.add_points(1)
        self.assertEquals(p.points,6001)
        self.assertEquals(p.get_level(),7)
        p.add_points(999)
        self.assertEquals(p.points,7000)
        self.assertEquals(p.get_level(),7)
        #level 8: 7001-8000
        p.add_points(1)
        self.assertEquals(p.points,7001)
        self.assertEquals(p.get_level(),8)
        p.add_points(999)
        self.assertEquals(p.points,8000)
        self.assertEquals(p.get_level(),8)
        #level 9: 8001-9000
        p.add_points(1)
        self.assertEquals(p.points,8001)
        self.assertEquals(p.get_level(),9)
        p.add_points(999)
        self.assertEquals(p.points,9000)
        self.assertEquals(p.get_level(),9)
        #level 10: 9001-...
        p.add_points(1)
        self.assertEquals(p.points,9001)
        self.assertEquals(p.get_level(),10)
        p.add_points(999)
        self.assertEquals(p.points,10000)
        self.assertEquals(p.get_level(),10)
        p.add_points(1000)
        self.assertEquals(p.points,11000)
        self.assertEquals(p.get_level(),10)

    def test_upload_moderate(self):
        """
        veririca que sólo las fotos moderadas den 10 puntos a los usuarios
        """
        #crea una temporada
        t, created=models.Temporada.objects.get_or_create(
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()+timedelta(days=1),
            titulo=self._get_random_string(10),
            descripcion=self._get_random_string(10),)

        #crea 10 foto
        for i in xrange(1,11):
            self._create_foto("E")

        #modera las fotos
        for i in xrange(1,11):
            foto=models.Foto.objects.get(id=i)
            #print foto.codigo_user.get_profile().points
            foto.estado = "M"
            foto.save()
            #print foto.codigo_user.get_profile().points
            self.assertEquals(foto.codigo_user.get_profile().points, 10)
            
    def test_vote(self):
        """
        verifica que los votos den a los votantes 2 puntos y a los votados 1 
        punto
        """
        from django.contrib.auth import authenticate, login        
        #crea una temporada
        t, created=models.Temporada.objects.get_or_create(
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()+timedelta(days=1),
            titulo=self._get_random_string(10),
            descripcion=self._get_random_string(10),)

        #crea 10 foto
        for i in xrange(1,11):
            self._create_foto()
        
        #vota por las 10 fotos:
        for i in xrange(1,11):
            uname = self._get_random_string(5)
            user = self._create_user(uname)
            ##ese codigo era para probarla vista json_me_gusta pero por alguna
            #razon alejecutarse no pasaba nada en a db
            # result=self.client.login(username=user.username,
            #                          password='123')
            # self.assertTrue(
            #     result,
            #     "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
            # response = self.client.get('/json_me_gusta/'+str(i)+'/',
            #                            HTTP_HOST='127.0.0.1:8082')
            # print response.content
            # #self.client.logout()
            # self.assertEqual(response.status_code, 200)
            foto = models.Foto.objects.get(id=i)
            temp_actual = models.Temporada().get_current_temporada()
            if temp_actual:
                if foto not in user.get_profile().get_photos_voted_from_this_temporada(temp_actual):
                    new_voto = models.Voto(codigo_user=user,
                                           codigo_foto=foto,
                                           codigo_temporada=temp_actual)
                    new_voto.save()
                    user.get_profile().nuevo_voto()
                    foto.add_num_favoritos()
                    models.Estadistica.objects.get_or_create(id=1)[0].add_voto()
                    new_voto.increasePoints()
            
            self.assertEqual(
                models.UserProfile.objects.get(id=user.id).points, 
                2)
            self.assertEqual(
                models.Foto.objects.get(id=i).codigo_user.get_profile().points,
                11)            

    def test_make_friends(self):
        """
        verifica que cuando 2 usuarios se hacen amigos ambos reciban 5 puntos
        """
        from fotos.forms import AddFriendForm, AcceptSolicitude
        #crea 2 usuarios
        user1 = self._create_user(self._get_random_string(5))
        user2 = self._create_user(self._get_random_string(5))
        
        #crea la solicitud de amistad de user1 a user2
        form = AddFriendForm({'amigo':user2.id})
        if form.is_valid(user1):
            form.save(user1)

        #user2 acepta la solicitud de amistad de user 1
        form = AcceptSolicitude({'amigo': user1.id})
        if form.is_valid():
            form.save(user2)

        #verifica que ambos usuarios tengan 5 puntos extra
        self.assertEquals(user1.get_profile().points,5)
        self.assertEquals(user2.get_profile().points,5)

    def test_foro_create_topic(self):
        """
        verifica que al crear un nuevo tema en el foro se agregen 5 puntos al
        usuario
        """
        from djangobb_forum.models import Forum, Topic, Category
        from djangobb_forum.forms import AddPostForm
        from django.shortcuts import get_object_or_404
        #crea un usuario
        user = self._create_user(self._get_random_string(5))
        #crea un foro
        category, created = Category.objects.get_or_create(
            name=self._get_random_string(5))
        foro, created = Forum.objects.get_or_create(
            name=self._get_random_string(5),
            category=category)
        #crea un tema en el foro
        form = AddPostForm({'name':self._get_random_string(5), 
                            'body':self._get_random_string(10)},
                           {},
                           topic=None, 
                           forum=get_object_or_404(Forum, pk=foro.id),
                           user=user,
                           ip='127.0.0.1')
        self.assertTrue(form.is_valid(),
                        'el formulario AddPostForm no es válido')
        form.save()
        
        #verifica que el usuario haya recibido 5 puntos extra
        self.assertEquals(models.User.objects.get(id=user.id).get_profile().points,5)

    def test_foro_response_a_topic(self):
        """
        verifica que cuando un usuario responde a un tema reciba 2 puntos
        """            
        from djangobb_forum.models import Forum, Topic, Category
        from djangobb_forum.forms import AddPostForm
        from django.shortcuts import get_object_or_404
        #crea un usuario
        user = self._create_user(self._get_random_string(5))
        user2 = self._create_user(self._get_random_string(5))
        #crea un foro
        category, created = Category.objects.get_or_create(
            name=self._get_random_string(5))
        foro, created = Forum.objects.get_or_create(
            name=self._get_random_string(5),
            category=category)
        #crea un tema en el foro
        form = AddPostForm({'name':self._get_random_string(5), 
                            'body':self._get_random_string(10)},
                           {},
                           topic=None, 
                           forum=get_object_or_404(Forum, pk=foro.id),
                           user=user,
                           ip='127.0.0.1')
        self.assertTrue(form.is_valid(),
                        'el formulario AddPostForm no es válido')
        form.save()
        #crea 2 post en tema
        form = AddPostForm({'body':self._get_random_string(10)},
                           {},
                           topic=Topic.objects.get(id=1), 
                           forum=None,
                           user=user,
                           ip='127.0.0.1')
        self.assertTrue(form.is_valid(),
                        'el formulario AddPostForm no es válido')
        form.save()
        
        form = AddPostForm({'body':self._get_random_string(10)},
                           {},
                           topic=Topic.objects.get(id=1), 
                           forum=None,
                           user=user2,
                           ip='127.0.0.1')
        self.assertTrue(form.is_valid(),
                        'el formulario AddPostForm no es válido')
        form.save()
        #verifica que los usuarios hayan recibido 2 puntos extra
        self.assertEquals(
            models.User.objects.get(id=user.id).get_profile().points,7)
        self.assertEquals(
            models.User.objects.get(id=user2.id).get_profile().points,2)        

    def test_reputation(self):
        """
        verifica que cuando un usuario use el sistema de reputación reciba 1
        punto
        """            
        from django.contrib.auth import login        
        from djangobb_forum.models import Forum, Topic, Category
        from djangobb_forum.forms import AddPostForm, ReputationForm
        from django.shortcuts import get_object_or_404
        #crea dos usuarios
        user = self._create_user(self._get_random_string(5))
        user2 = self._create_user(self._get_random_string(5))
        #crea un foro
        category, created = Category.objects.get_or_create(
            name=self._get_random_string(5))
        foro, created = Forum.objects.get_or_create(
            name=self._get_random_string(5),
            category=category)
        #crea un tema en el foro
        form = AddPostForm({'name':self._get_random_string(5), 
                            'body':self._get_random_string(10)},
                           {},
                           topic=None, 
                           forum=get_object_or_404(Forum, pk=foro.id),
                           user=user,
                           ip='127.0.0.1')
        self.assertTrue(form.is_valid(),
                        'el formulario AddPostForm no es válido')
        form.save()
        #crea 1 post en tema
        form = AddPostForm({'body':self._get_random_string(10)},
                           {},
                           topic=Topic.objects.get(id=1), 
                           forum=None,
                           user=user,
                           ip='127.0.0.1')
        self.assertTrue(form.is_valid(),
                        'el formulario AddPostForm no es válido')
        form.save()
        
        #usuario 2 aniade un punto a la reputación de user 1
        form = ReputationForm({'reason':'jiji',
                               'post':1,
                               'sign':1},
                              from_user=user2, to_user=user)
        # form.is_valid()
        # print form.errors

        self.assertTrue(form.is_valid(),
                        'el formulario ReputationForm no es válido')
        form.save()
                
        #verifica que user2 recibio un punto extra
        userprofile2 = models.UserProfile.objects.get(id=2)
        self.assertEqual(userprofile2.points, 
                         1,
                         "user2 points: "+str(userprofile2.points)+", it should be: 1")


    def test_send_email(self):
        """
        Verifica que al enviar un mail desde el foro, el usuario reciba un punto
        """       
        from django.contrib.auth import login        
        #crea dos usuarios
        user = self._create_user(self._get_random_string(5))
        user2 = self._create_user(self._get_random_string(5))
        
        #logea al usuario 'user'
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))

        #envia un mail de user a user2
        response = self.client.post('/bb/forum/misc/?mail_to=%s' % user2.username,
                                    {'subject':'tmre', 
                                     'body':'ajo!', 
                                     'submit':''},
                                    HTTP_HOST='127.0.0.1:8082')
        #print response.content
        #self.client.logout()
        self.assertEqual(response.status_code, 302)

        #verifica que se halla incrementado el puntaje de user en 1
        self.assertEqual(models.UserProfile.objects.get(id=user.id).points,1)

    def test_send_private_email(self):
        """
        Verifica que al enviar un mensaje privado desde el foro, 
        el usuario reciba un punto
        """       
        from django.contrib.auth import login        
        #crea dos usuarios
        user = self._create_user(self._get_random_string(5))
        user2 = self._create_user(self._get_random_string(5))
        
        #logea al usuario 'user'
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))

        #envia un mensaje privado de user a user2
        response = self.client.post('/bb/forum/pm/compose/admin/',
                                    {'recipient':user2.username,
                                     'subject':'tmre', 
                                     'body':'ajo!', 
                                     'submit':''},
                                    HTTP_HOST='127.0.0.1:8082')
        #print response.content
        #self.client.logout()
        self.assertEqual(response.status_code, 302)

        #verifica que se halla incrementado el puntaje de user en 1
        self.assertEqual(models.UserProfile.objects.get(id=user.id).points,1)

    # def test_service_register(self):
    #     """
    #     Verifica que al registrarse un servicio, recibe 20 puntos
    #     del sistema de badges
    #     """       
    #     from django.contrib.auth import authenticate, login        
    #     from djangobb_forum.models import Forum, Topic, Category
    #     from djangobb_forum.forms import AddPostForm, ReputationForm
    #     from django.shortcuts import get_object_or_404
    #     from servicios.models import TipoServicio, Servicio
    #     #crea un nuevo tipo de servicio
    #     ts, created = TipoServicio.objects.get_or_create(nombre='s1')        
        
    #     #registra un nuevo servicio
    #     name = self._get_random_string(5)
    #     response = self.client.post('/servicios/registro/',
    #                                 {'nombre':name,
    #                                  'tipo_servicio':ts.id,
    #                                  'foto_principal':'',
    #                                  'email':'%s@mail.com' % name,
    #                                  'contrasenia':'123',
    #                                  'terminos':True,
    #                                  'direccion':name,
    #                                  'latitud':12,
    #                                  'longitud':12,
    #                                  'instance':'',
    #                                  'submit':''},
    #                                 HTTP_HOST='127.0.0.1:8082')
    #     print response.content
    #     self.assertEqual(response.status_code, 302)

    #     #verifica que se halla incrementado el puntaje de user en 20
    #     self.assertEqual(models.UserProfile.objects.get(id=user.id).points,20)


    def test_make_opinion(self):
        """
        Verifica que al escribir una opinion en un servicio, el usuario 
        recibe 5 puntos del sistema de badges
        """       
        from django.contrib.auth import login        
        from servicios.models import TipoServicio, Servicio
        #crea un usuario
        user = self._create_user(self._get_random_string(5))

        #crea un nuevo tipo de servicio
        ts, created = TipoServicio.objects.get_or_create(nombre='s1')        
        
        #registra un nuevo servicio
        name = self._get_random_string(5)
        f=open('%s/public/media/dump_images/face_woman.png' % settings.BASEDIR,'rb')
#        print f;
        response = self.client.post(reverse('ser_registro'),
                                    {'nombre':name,
                                     'tipo_servicio':ts.id,
                                     'foto_principal':f,
#                                      'foto_principal':u'%s/public/media/dump_images/face_woman.png' % settings.BASEDIR,
                                     'email':'%s@mail.com' % name,
                                     'contrasenia':'123',
                                     'idioma':'es',
                                     'terminos':True,
                                     'direccion':name,
                                     'latitud':12,
                                     'longitud':12,
                                     'instance':'',
                                     'recaptcha_challenge_field':'',
                                     'recaptcha_response_field':'',
                                     'appTest':'',
                                     'submit':''},
                                    HTTP_HOST='127.0.0.1:8082')
        f.close()
        
        #print response.content
        self.assertEqual(Servicio.objects.count(),1)
        self.assertEqual(response.status_code, 200)

        #marca el servicio como aceptado
        servicio = Servicio.objects.all()[0]
        servicio.estado=u'A'
        servicio.save()

        #logea al usuario 'user'
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        
        #crea una opinion al servicio registrado
        response = self.client.post(reverse('ser_perfil_publico',args=[servicio.id]),
                                    {'usuario':user.id,
                                     'servicio':servicio.id,
                                     'texto':'jiji',
                                     'puntuacion':5,
                                     'valoracion':0,
                                     'opinion':'',
                                     },
                                    HTTP_HOST='127.0.0.1:8082')
        #print response.content
        self.assertEqual(response.status_code, 200)

        #verifica que se halla incrementado el puntaje de user en 5
        self.assertEqual(models.UserProfile.objects.get(id=user.id).points,5)

    def test_using_contactForm(self):
        """
        Verifica que el formulario de contacto en un servicio, el usuario 
        recibe 5 puntos del sistema de badges
        """       
        from servicios.models import TipoServicio, Servicio
        #crea un usuario
        user = self._create_user(self._get_random_string(5))

        #crea un nuevo tipo de servicio
        ts, created = TipoServicio.objects.get_or_create(nombre='s1')        
        
        #registra un nuevo servicio
        name = self._get_random_string(5)
        f=open('%s/public/media/dump_images/face_woman.png' % settings.BASEDIR,'rb')
        response = self.client.post('/servicios/registro/',
                                    {'nombre':name,
                                     'tipo_servicio':ts.id,
                                     'foto_principal':f,
                                     #'foto_principal':'images/social/Twitter.png',
                                     'email':'%s@mail.com' % name,
                                     'contrasenia':'123',
                                     'idioma':'es',
                                     'terminos':True,
                                     'direccion':name,
                                     'latitud':12,
                                     'longitud':12,
                                     'instance':'',
                                     'recaptcha_challenge_field':'',
                                     'recaptcha_response_field':'',
                                     'appTest':'',
                                     'submit':''},
                                    HTTP_HOST='127.0.0.1:8082')
        f.close()
        #poniendo el servicio en estado aceptado
        servicio = Servicio.objects.all()[0]
        servicio.estado=u'A'
        servicio.save()

        #print response.content
        self.assertEqual(Servicio.objects.count(),1)
        #print "%s" % str(Servicio.objects.all()[0].id)
        self.assertEqual(response.status_code, 200)

        #logea al usuario 'user'
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))

        #usa el contacFrom del servicio registrado
        response = self.client.post('/servicios/%s/' % servicio.id,
                                    {'nombre':user.username,
                                     'email':user.email,
                                     'mensaje':'jijiji',
                                     'contacto':'',
                                     },
                                    HTTP_HOST='127.0.0.1:8082')
        #print response.content
        self.assertEqual(response.status_code, 200)

        #verifica que se halla incrementado el puntaje de user en 5
        self.assertEqual(models.UserProfile.objects.get(id=user.id).points,5)

class UserProfileActivityStreamTest(BaseOperations):
    def test_no_activities(self):
        """
        verifica que la url /usuario/ funcione correctamente cuando no
        hay ninguna actividad que mostrar
        """
        #registra un usuario
        user = self._create_user(self._get_random_string(5))
        #logea al usuario y verifica que el exito del logeo
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verifica que la página se muestre correctamente
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)
    def test_votes(self):
        """
        verifica que la url /usuario/ no produzca errores por la falta
        o abundancia de votos
        """
        #crea una temporada
        t, created=models.Temporada.objects.get_or_create(
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()+timedelta(days=1),
            titulo=self._get_random_string(10),
            descripcion=self._get_random_string(10),)
        #crea 5 usuarios
        for i in xrange(5):
            user = self._create_user(self._get_random_string(5))
        #sube 5 fotos por cada usuario
        for u in models.User.objects.all():
            for i in xrange(5):
                self._create_foto_for(u)
        #los usuarios votan de manera random por las fotos del usuario con id=1
        user = models.User.objects.get(id=1)
        photos_list = user.fotos.all()
        for u in models.User.objects.all():
            self._create_voto(u,random.choice(photos_list),t)
        #logea al usuario con id=1 y verifica su logeo exitoso
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verifica que la página se muestre correctamente
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)

    def test_friends_uploads(self):
        """
        verifica que la url /usuario/ se muestre correctamente cuando los
        amigos del usuario subieron fotos
        """
        #crea una temporada
        t, created=models.Temporada.objects.get_or_create(
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()+timedelta(days=1),
            titulo=self._get_random_string(10),
            descripcion=self._get_random_string(10),)
        #crea 5 usuarios
        for i in xrange(5):
            user = self._create_user(self._get_random_string(5))
        #todos se hacen amigos del usuario con id=1 
        user = models.User.objects.get(id=1)
        for i in xrange(2,6):
            user.get_profile().amigos.add(models.UserProfile.objects.get(id=i))
        #sube 5 fotos por cada usuario
        for u in models.User.objects.all():
            for i in xrange(5):
                self._create_foto_for(u)
        
        #logea al usuario con id=1 y verifica su logeo exitoso
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verifica que la página se muestre correctamente
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)
        
    def test_topics_answers(self):
        from djangobb_forum.models import Category, Forum, Topic, Post
        """
        verifica que la url /usuario/ se muestre correctamente cuando se 
        responde un topic creado por el usuario
        """
        #crea 5 usuarios
        for i in xrange(5):
            user = self._create_user(self._get_random_string(5))
        #crea un foro
        category, created = Category.objects.get_or_create(
            name='categoria1', position=0)
        forum, crated = Forum.objects.get_or_create(
            category=category, name='foro1',)
        self.assertEqual(Forum.objects.count(),1)
        #crea 5 topics del usuario con id=1
        user = models.User.objects.get(id=1)
        for i in xrange(5):
            Topic.objects.create(forum=forum,
                                 name=self._get_random_string(5),
                                 user=user,)
        self.assertEqual(Topic.objects.count(),5)
        #logea al usuario con id=1 y verifica su logeo exitoso
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verificando que la url se muestra correctamente cuando hay topics 
        #creados pero no posts
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)
        #todos los usuarios escriben una respuesta en un topic random del 
        #usuario con id=1
        topics = user.topic_set.all()
        for i in xrange(1,6):
            Post.objects.create(topic=random.choice(topics),
                                user=models.User.objects.get(id=i),
                                markup='bbcode',
                                body='qwe',
                                body_html='qwe',)
        self.assertEqual(Post.objects.count(),5)
        #logea al usuario con id=1 y verifica su logeo exitoso
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verifica que la página se muestre correctamente
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)

    def test_new_services(self):
        """
        verifica que la url /usuario/ se muestre correctamente cuando se 
        muestran nuevos servicios registrados
        """
        from servicios.models import Servicio, TipoServicio, Ubicacion
        #crea un usuario
        user = self._create_user(self._get_random_string(5))        
        #crea una nueva ubicación
        location, created = Ubicacion.objects.get_or_create(
            direccion='qweqwe',latitud=11,longitud=11)
        self.assertTrue(created)
        #crea un nuevo tipo de servicio
        ts, created = TipoServicio.objects.get_or_create(
            nombre='ts1',
            icono='images/social/Twitter.png')
        self.assertTrue(created)
        #crea 5 nuevos servicios
        for i in xrange(5):
            Servicio.objects.create(nombre=self._get_random_string(5),
                                    tipo_servicio=ts,
                                    foto_principal='images/social/Twitter.png',
                                    ubicacion=location,
                                    puntuacion=0,
                                    num_visitas=0,
                                    num_opiniones=0,
                                    destacado=False)
        self.assertEqual(Servicio.objects.count(),5)
        #logea al usuario con id=1 y verifica su logeo exitoso
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verifica que la página se muestre correctamente
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)
        
    def test_friends_levels(self):
        """
        verifica que la url /usuario/ se muestre correctamente cuando se 
        muestran los nuevos niveles alcanzados por los amigos del usuario
        """
        #crea 5 usuarios
        for i in xrange(5):
            user = self._create_user(self._get_random_string(5))        
        #todos se hacen amigos del usuario con id=1
        user = models.User.objects.get(id=1)
        for i in xrange(2,6):
            user.get_profile().amigos.add(models.UserProfile.objects.get(id=i))
        #logea al usuario con id=1 y verifica su logeo exitoso
        result=self.client.login(username=user.username,
                                 password='123')
        self.assertTrue(
            result,
            "loggedIn:%s  username:%s is_active:%s" % (str(result),user.username,str(user.is_active)))
        #verifica que la página se muestre correctamente
        response = self.client.get('/usuario/',{},HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(
            response.status_code, 200, 'status_code:%s' % response.status_code)
        
        
class FotosTest(BaseOperations):
    def test_upload_vote(self):
        """
        prueba que una foto subida dentro de un periodo de votación
        este habilitada para ser votada,
        """
        #crea una temporada
        t, created=models.Temporada.objects.get_or_create(
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now()+timedelta(days=1),
            titulo=self._get_random_string(10),
            descripcion=self._get_random_string(10),)

        #crea 10 fotos
        for i in xrange(1,11):
            self._create_foto()
        
        #evalua si las fotos estan habilitadas para el periodo de votacion
        for i in xrange(1,11):
            foto=models.Foto.objects.get(id=i)
            self.assertEquals(foto.temporada_habilitado, "S")


class TemporadasTest(TestCase):
    def _create_user(self, username):
        from django.contrib.auth.models import User
        user, created = User.objects.get_or_create(username=username)
        return user
    
    def _get_random_string(self, length):
        import string
        return ''.join(random.choice(string.letters) for i in xrange(length))

    def _create_foto(self):
        uname = self._get_random_string(20)
        user = self._create_user(uname)
        categoria, created = models.Categoria.objects.get_or_create(
            nombre='nombre1',
            nombre_espaniol='nombre_espaniol',
            descripcion='descripcion',
            descripcion_espaniol='descripcion_espaniol')
        #print "creating foto for user %s" % uname 
        models.Foto.objects.create(estado='M',
                                   temporada_habilitado='S',
                                   codigo_user=user,
                                   categoria=categoria,
                                   titulo='titulo',
                                   foto='images/social/Twitter.png',
                                   )
        profile = user.get_profile()
        profile.uploaded_photos=1
        profile.save()

    def _create_vote(self, user, foto):
        import datetime
        temp_actual = models.Temporada().get_current_temporada()
        if temp_actual and temp_actual.is_in_this_temporada(datetime.datetime.now()):
            new_voto = models.Voto(codigo_user=user,
                            codigo_foto=foto,
                            codigo_temporada=temp_actual)
            new_voto.save()             
            user.get_profile().nuevo_voto()
            foto.add_num_favoritos()            
        
    def test_start_temporada(self):
        from fotos.models import start_temporada
        from django.contrib.auth.models import User
        test_user = self._create_user('juan')
        profile = test_user.get_profile()
        profile.uploaded_photos = 4
        profile.save()
        test_user2 = self._create_user('juan2')
        profile = test_user2.get_profile()
        profile.uploaded_photos = 0
        profile.save()
        start_temporada()
        # reload users
        test_user = User.objects.get(pk=test_user.pk)
        test_user2 = User.objects.get(pk=test_user2.pk)
        self.assertEquals(test_user.get_profile().uploaded_photos, 0)
        self.assertEquals(test_user2.get_profile().uploaded_photos, 0)
        # make user all users have uploaded photos at 0
        self.assertEquals(
            models.UserProfile.objects.all().count(),
            models.UserProfile.objects.filter(uploaded_photos=0).count())


    def test_get_current_temporada(self):
        import datetime
        # delete all temporadas, sholud return ''
        models.Temporada.objects.all().delete()
        self.assertEquals(models.Temporada().get_current_temporada(), '')
        # create 3 temporadas one already closed, one active and ending in 2
        # days, and one starting in 2 days and ending in 5 days
        now = datetime.datetime.now()
        models.Temporada.objects.create(
            fecha_inicio = now - datetime.timedelta(days=2),
            fecha_fin = now - datetime.timedelta(days=1),
            titulo = 'past')
        models.Temporada.objects.create(
            fecha_inicio = now - datetime.timedelta(days=1),
            fecha_fin = now + datetime.timedelta(days=2),
            titulo = 'present')
        models.Temporada.objects.create(
            fecha_inicio = now + datetime.timedelta(days=2),
            fecha_fin = now + datetime.timedelta(days=5),
            titulo = 'future')
        self.assertEquals(models.Temporada().get_current_temporada().titulo,
                          'present')
        models.Temporada.objects.filter(titulo='present').delete()
        self.assertEquals(models.Temporada().get_current_temporada().titulo,
                          'future')
        models.Temporada.objects.create(
            fecha_inicio = now + datetime.timedelta(days=1),
            fecha_fin = now + datetime.timedelta(days=4),
            titulo = 'future_reloaded')
        self.assertEquals(models.Temporada().get_current_temporada().titulo,
                          'future_reloaded')
        models.Temporada.objects.filter(titulo='future').delete()
        models.Temporada.objects.filter(titulo='future_reloaded').delete()
        self.assertEquals(models.Temporada().get_current_temporada(), '')
        
    def test_close_temporada(self):
        def create_vote_on_random_foto(temporada, user=None):
            if not user:
                uname = self._get_random_string(20)
                user = self._create_user(uname)
            # vote just on the first 20 fotos, so they should win
            foto = models.Foto.objects.get(pk=random.randint(1, 20))
            foto.num_favoritos += 1
            foto.save()
            models.Voto.objects.create(codigo_user=user,
                                       codigo_foto=foto,
                                       codigo_temporada=temporada)
            #print 'user %s voted on foto %s' % (uname, foto.pk)
            
        # create 100 fotos
        for i in xrange(0, 100):
            self._create_foto()

        self.assertEquals(models.Foto.objects.count(), 100)
        # create 1000 votes on the images

        # create a temporada object
        import datetime
        now  = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        ten_days_ago = now - datetime.timedelta(days=30)
        temporada = models.Temporada.objects.create(
            fecha_inicio=ten_days_ago,
            fecha_fin=yesterday,
            titulo='test')
            
        for i in xrange(0, 90):
            create_vote_on_random_foto(temporada)

        user = self._create_user('testuser')
        for i in xrange(0, 990):
            create_vote_on_random_foto(temporada, user)
            
        models.close_temporada()
        # verify the foto winners have the highest votes
        winners = temporada.foto_set.all().order_by('-num_favoritos')
        all_fotos = models.Foto.objects.filter()
        for w in winners:
            from django.db.models import Max
            max_votes = all_fotos.aggregate(Max('num_favoritos'))
            max_votes = max_votes['num_favoritos__max']
            self.assertEquals(max_votes, w.num_favoritos)
            all_fotos = all_fotos.exclude(pk=w.pk)

        # verify the random vote winners selecion make sense
        # testuser voted 950 of 1000 times, he shuold win
        #test_win = models.Ganador_Votos.objects.filter(temporada=temporada,
        #                                    user=user).count()
        #self.assertEquals(test_win, 1)

    def test_report_firstVP(self):
        import datetime
        # delete all temporadas, sholud return ''
        models.Temporada.objects.all().delete()
        self.assertEquals(models.Temporada().get_current_temporada(), '')
        # create one temporada starting 1 day on the future
        now = datetime.datetime.now()
        models.Temporada.objects.create(
            fecha_inicio = now + datetime.timedelta(days=1),
            fecha_fin = now + datetime.timedelta(days=2),
            titulo = 'tmp')

        # create 10 fotos
        for i in xrange(0, 10):
            self._create_foto()
                        
        #create 10 accepted photo reports
        for i in xrange(0,10):
            d = models.Denuncia(codigo_foto = models.Foto.objects.get(id=i+1),
                                codigo_user = models.User.objects.get(id=i+1),
                                codigo_temporada = models.Temporada().get_current_temporada(),
                                razon=u'1',
                                respuesta=u'A')
            d.save()
        #reviewing that everyone recovered their photo upload
        good = True
        for u in models.UserProfile.objects.all():
            if int(u.uploaded_photos) != 0:
                good = False
                break
        self.assertTrue(good, "one VP in the futures: not all users recovered their possibilities of uploading photos")
       

        #creates 10 new photos
        for i in xrange(0, 10):
            self._create_foto()
        
        #modifies the start date of the temporada to begins now
        current_temp = models.Temporada().get_current_temporada()
        current_temp.fecha_inicio = now
        current_temp.save()
        
        # create 10 votes
        for i in xrange(11,21):
            self._create_vote(models.User.objects.get(id=i), models.Foto.objects.get(id=i))

        #create 10 accepted photo reports
        for i in xrange(11,21):
            d = models.Denuncia(codigo_foto = models.Foto.objects.get(id=i),
                                codigo_user = models.User.objects.get(id=i),
                                codigo_temporada = models.Temporada().get_current_temporada(),
                                razon=u'1',
                                respuesta=u'A')
            d.save()
        #reviewing that everyone recovered their photo upload
        good = True
        for u in models.UserProfile.objects.all():
            if int(u.uploaded_photos) != 0:
                good = False
                break
        self.assertTrue(good, "one VP in the present: not all users recovered their possibilities of uploading photos")


    def test_report_firstVP_2(self):
        """
        simula cuando se acabaron las temporadas de votacion y hay reportes de
        fotos creados tanto dentro de la temporada que finalizo como despues de
        la temporada
        """
        import datetime
        # delete all temporadas, sholud return ''
        models.Temporada.objects.all().delete()
        self.assertEquals(models.Temporada().get_current_temporada(), '')
        # create one temporada starting 1 day on the future
        now = datetime.datetime.now()
        models.Temporada.objects.create(
            fecha_inicio = now + datetime.timedelta(days=1),
            fecha_fin = now + datetime.timedelta(days=2),
            titulo = 'tmp')

        #creates 10 new photos
        for i in xrange(0, 10):
            self._create_foto()

        # create 10 votes
        for i in xrange(1,11):
            self._create_vote(models.User.objects.get(id=i), models.Foto.objects.get(id=i))

        #create 5 photo reports
        for i in xrange(1,6):
            d = models.Denuncia(codigo_foto = models.Foto.objects.get(id=i),
                                codigo_user = models.User.objects.get(id=i),
                                codigo_temporada = models.Temporada().get_current_temporada(),
                                razon=u'1',
                                respuesta=u'E')
            d.save()

        #modifies the starting and ending date of the temporada
        #to create a finished temporada
        current_temp = models.Temporada().get_current_temporada()
        current_temp.fecha_inicio = datetime.datetime.now() - datetime.timedelta(days=2)
        current_temp.fecha_fin = datetime.datetime.now() - datetime.timedelta(days=1)
        current_temp.save()

        #sets to 0 the uploaded photo counters from user profiles
        for u in models.UserProfile.objects.all():
            u.reset_uploaded_photos()

        #accepting the reports after the temporada is closet
        for r in models.Denuncia.objects.filter(respuesta=u'E'):
            r.respuesta=u'A'
            r.save()

        #reviewing that no one recovered their photo upload
        good = True
        for u in models.UserProfile.objects.all():
            if int(u.uploaded_photos) != 0:
                good = False
                break
        self.assertTrue(good, "one VP in the past 1: It is no supposed users recover their possibilities of uploading photos")

        #create 5 accepted photo reports
        for i in xrange(6,11):
            d = models.Denuncia(codigo_foto = models.Foto.objects.get(id=i),
                                codigo_user = models.User.objects.get(id=i),
                                razon=u'1',
                                respuesta=u'A')
            d.save()

        #reviewing that no one recovered their photo upload
        good = True
        for u in models.UserProfile.objects.all():
            if int(u.uploaded_photos) != 0:
                good = False
                break
        self.assertTrue(good, "one VP in the past 2: It is no supposed users recover their possibilities of uploading photos")

    def test_report_betweenVP_2(self):
        """
        simula cuando hay reportes entre temporadas
        creados en tmp1 moderados en tmp2
        """
        import datetime
        # delete all temporadas, sholud return ''
        models.Temporada.objects.all().delete()
        self.assertEquals(models.Temporada().get_current_temporada(), '')
        # create one temporada starting 1 day on the future
        now = datetime.datetime.now()
        models.Temporada.objects.create(
            fecha_inicio = now + datetime.timedelta(days=1),
            fecha_fin = now + datetime.timedelta(days=2),
            titulo = 'tmp1')

        #creates 10 new photos
        for i in xrange(0, 10):
            self._create_foto()

        # create 10 votes
        for i in xrange(1,11):
            self._create_vote(models.User.objects.get(id=i), models.Foto.objects.get(id=i))

        #create 10 photo reports
        for i in xrange(1,11):
            d = models.Denuncia(codigo_foto = models.Foto.objects.get(id=i),
                                codigo_user = models.User.objects.get(id=i),
                                codigo_temporada = models.Temporada().get_current_temporada(),
                                razon=u'1',
                                respuesta=u'E')
            d.save()
        
        #modifies the starting and ending date of the temporada
        #to create a finished temporada
        current_temp = models.Temporada().get_current_temporada()
        current_temp.fecha_inicio = datetime.datetime.now() - datetime.timedelta(days=2)
        current_temp.fecha_fin = datetime.datetime.now() - datetime.timedelta(days=1)
        current_temp.save()
    
        #modifies the date of fotos to be accord with the temporada just mudified
        for f in models.Foto.objects.all():
            f.fecha = datetime.datetime.now() - datetime.timedelta(days=2)

        #sets to 0 the uploaded photo counters from user profiles
        for u in models.UserProfile.objects.all():
            u.reset_uploaded_photos()        
        
        # create a temporada starting now
        now = datetime.datetime.now()
        models.Temporada.objects.create(
            fecha_inicio = now,
            fecha_fin = now + datetime.timedelta(days=1),
            titulo = 'tmp2')
        
        #accepting the reports done in the previous temporada
        for r in models.Denuncia.objects.filter(respuesta=u'E'):
            r.respuesta=u'A'
            r.save()

        #reviewing that no one recovered their photo upload
        good = True
        for u in models.UserProfile.objects.all():
            if int(u.uploaded_photos) != 0:
                good = False
                break
        self.assertTrue(good, "VP3: It is no supposed users recover their possibilities of uploading photos")
        
        
