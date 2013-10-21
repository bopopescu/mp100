# -*- coding: utf-8 -*-

from django.test import TestCase
from django.conf import settings
from servicios.models import *


class ServiciosTest(TestCase):
    def _create_user(self, username, is_active=True):
        """
        Crea un nuevo usuario
        """
        user, created = User.objects.get_or_create(username=username,
                                                   email=username+'@user.com',
                                                   is_active=is_active)
        user.set_password('123')
        user.save()

        return user

    def _create_tipo_servicio(self, nombre):
        """
        Crea un nuevo tipo de servicio
        """
        if TipoServicio.objects.filter(nombre=nombre):
            tipo_servicio = TipoServicio.objects.get(nombre=nombre)
        else:
            tipo_servicio = TipoServicio(nombre=u"%s" % nombre)
            tipo_servicio.save()

        return tipo_servicio

    def _create_servicio_publico(self, nombre,
                                 nombre_tipo_servicio=u"NuevoTipoServicio",
                                 direccion=u"Dirección", latitud=1, longitud=1):
        """
        Crea un servicio público
        """
        tipo_servicio = self._create_tipo_servicio(nombre_tipo_servicio)
        ubicacion = Ubicacion(direccion=direccion,
                              latitud=latitud, longitud=longitud)
        ubicacion.save()
        servicio = Servicio(nombre=u"%s" % nombre,
                            tipo_servicio=tipo_servicio,
                            ubicacion=ubicacion,
                            estado=u"A")
        servicio.save()

        return servicio

    def _create_servicio(self, nombre, is_active=True):
        """
        Crea un servicio de prueba
        """
        import random
        import sha

        servicio = self._create_servicio_publico(nombre)

        salt = sha.new(str(random.random())).hexdigest()[:5]
        key = sha.new(salt+"cadena_texto").hexdigest()
        admin = AdministradorServicio(user=self._create_user(nombre, is_active),
                                      servicio=servicio,
                                      clave_activacion=key)
        admin.save()

        return servicio, admin

    def _create_opinion(self, servicio):
        """
        Crea una nueva opinion para un servicio
        """
        usuario = self._create_user("Usuario")
        opinion = Opinion(usuario=usuario.get_profile(), servicio=servicio,
                          texto=u"Hola", moderado=True)
        opinion.save()

        return opinion

    def _create_actividad(self, tipo, servicio):
        """
        Crea una actividad relacionada al servicio
        """
        Actividad.register(tipo, servicio)

    def _compare_querysets(self, queryset_1, queryset_2):
        """
        Compara dos queryset de servicios
        """

        return list(queryset_1) == list(queryset_2)

    def test_num_visitas(self):
        """
        Verifica que el número de visitas se está incrementando para un servicio
        """
        (servicio, admin) = self._create_servicio("Nuevo")
        self.assertEqual(servicio.num_visitas, 0)
        # Primera entrada
        response = self.client.get("/servicios/%s/" % servicio.id,
                                    {},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.accepted.get(id=servicio.id).num_visitas, 1)
        # Segunda entrada
        response = self.client.get("/servicios/%s/" % servicio.id,
                                    {},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.accepted.get(id=servicio.id).num_visitas, 1)
        # logeo del usuario adminsitrador del servicio
        self.client.login(username=admin.user, password="123")
        response = self.client.get("/servicios/%s/" % servicio.id,
                                    {},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.accepted.get(id=servicio.id).num_visitas, 1)
        # logeo con otro username
        self.client.login(username=self._create_user("Otro"), password="123")
        response = self.client.get("/servicios/%s/" % servicio.id,
                                    {},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.accepted.get(id=servicio.id).num_visitas, 2)

    def test_servicio_publico(self):
        """
        Verifica la creación de un nuevo servicio sin administrador
        """
        f = open('%s/public/media/dump_images/dump_mt.jpg' % settings.BASEDIR)
        response = self.client.post("/servicios/",
                                    {"nombre": u"NuevoServicio",
                                     "tipo_servicio": self._create_tipo_servicio(u"NuevoTipoServicio").id,
                                     "direccion": u"Dirección",
                                     "latitud": 12,
                                     "longitud": 12,
                                     "nuevo_servicio": True,
                                     "foto_principal": f,
                                     'recaptcha_challenge_field': '',
                                     'recaptcha_response_field': '',
                                     'appTest': ''},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        servicio = Servicio.accepted.get(id=1)
        self.assertEqual(servicio.nombre, u"NuevoServicio")

    def test_cambio_password(self):
        """
        Verifica el cambio de password
        """
        (servicio, admin) = self._create_servicio("Nuevo")
        response = self.client.post("/servicios/cambio_password/%s/%s/" % \
                                    (admin.clave_activacion, "abc"),
                                    {},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 302)
        admin = AdministradorServicio.objects.get(user__username="Nuevo")
        self.assertEquals(admin.user.check_password("abc"), True)

    def test_servicio_privado(self):
        """
        Cambia un servicio público a uno privado
        """
        # Un servicio ya creado pasa a un administrador
        servicio_publico = self._create_servicio_publico("Nuevo")
        self.assertEqual(servicio_publico.id, 1)
        f = open('%s/public/media/dump_images/dump_mt.jpg' % settings.BASEDIR)
        response = self.client.post("/servicios/registro/",
                                    {"instance": 1,
                                     "nombre": servicio_publico.nombre,
                                     "email": "l@l.com",
                                     "contrasenia": "123",
                                     "tipo_servicio": 1,
                                     "terminos": True,
                                     "direccion": "Direccion",
                                     "latitud": 1,
                                     "longitud": 1,
                                     'foto_principal': f,
                                     'idioma': 'es',
                                     'recaptcha_challenge_field': '',
                                     'recaptcha_response_field': '',
                                     'appTest': '',},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        servicio_privado = Servicio.objects.get(id=1)
        servicio_privado.estado = u'A'
        servicio_privado.save()
        servicio_privado = Servicio.accepted.get(id=1)
        self.assertEqual(servicio_privado.id, 1)
        # Se trata de cambiar de administrador
        admin_1 = AdministradorServicio.objects.get(id=1)
        response = self.client.get("/servicios/registro/",
                                   {"instance": 1},
                                   HTTP_HOST='127.0.0.1:8082')
        admin_2 = AdministradorServicio.objects.get(servicio__id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(admin_1, admin_2)

    def test_verificar_usuario(self):
        """
        Validación de un usuario por su correo electrónico
        """
        (servicio, admin) = self._create_servicio(nombre="Verificado", is_active=False)
        response = self.client.get("/servicios/verificar_usuario/%s/" % \
                                   admin.clave_activacion, {},
                                   HTTP_HOST='127.0.0.1:8082')
        admin = AdministradorServicio.objects.get(id=1)
        self.assertEqual(admin.user.is_active, True)
        self.assertEqual(response.status_code, 302)

    def test_perfiles(self):
        """
        Búsqueda de servicios
        """
        from django.utils.translation import ugettext_lazy as _
        # Servicios de prueba
        self._create_servicio_publico("Conrat", "Alojamiento", "Arequipa, Peru", 11, 10)
        self._create_servicio_publico("Hotel 1", "Alojamiento", "Arequipa, Peru", 11, 10)
        self._create_servicio_publico("Hotel 2", "Alojamiento", "Arequipa, Peru", 11, 10)
        self._create_servicio_publico("Libertador", "Alojamiento", "Sachaca, Arequipa, Peru", 9, 5)
        self._create_servicio_publico("Cruz del sur", "Transporte", "Arequipa, Peru", 9, 10)
        self._create_servicio_publico("Oltursa", "Transporte", "Arequipa, Peru", 2, 3)

        # Primara búsqueda sin parametros
        (filtro, tipo_servicio) = ("puntuacion", None)
        response = self.client.post("/servicios/perfiles/%s/" % filtro, {},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        # La variable de sesión de búsqueda
        busqueda = {"direccion": _(u"all locations"), "tipo": None,
                    "latitud": "-16.3167", "longitud": "-71.55",
                    "filtro": u"puntuacion"}
        self.assertEqual(self.client.session["busqueda"], busqueda)
        # La variable de sesión de resultados
        resultados = Servicio.accepted.all()
        self.assertEqual(self._compare_querysets(self.client.session["resultados"], resultados), True)

        # Búsqueda para un tipo de servicio
        tipo_servicio = 1
        response = self.client.get("/servicios/perfiles/%s/%s/" % \
                                   (filtro, tipo_servicio),
                                   {},
                                   HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        # La variable de sesión de búsqueda
        busqueda = {"direccion": _(u"all locations"),
                    "tipo": TipoServicio.objects.get(id=1),
                    "latitud": "-16.3167", "longitud": "-71.55",
                    "filtro": "puntuacion"}
        self.assertEqual(self.client.session["busqueda"], busqueda)
        # La variable de sesión de resultados
        resultados = Servicio.accepted.all()
        self.assertEqual(self._compare_querysets(self.client.session["resultados"], resultados), True)

        # Búsqueda para un tipo de servicio
        response = self.client.get("/servicios/perfiles/%s/%s/" % \
                                   (filtro, tipo_servicio),
                                   {},
                                   HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        # La variable de sesión de búsqueda
        busqueda = {"direccion": _(u"all locations"),
                    "tipo": TipoServicio.objects.get(id=1),
                    "latitud": "-16.3167", "longitud": "-71.55",
                    "filtro": u"puntuacion"}
        self.assertEqual(self.client.session["busqueda"], busqueda)
        # La variable de sesión de resultados
        resultados = Servicio.accepted.all()
        self.assertEqual(self._compare_querysets(self.client.session["resultados"], resultados), True)
        # El conjunto de resultados con los filtros
        resultados = Servicio.accepted.filter(tipo_servicio__id=1)
        self.assertEqual(self._compare_querysets(response.context["all_results"], resultados), True)

        # Búsqueda para una ubicación específica y un tipo de servicio por post
        response = self.client.post("/servicios/perfiles/%s/%s/" % \
                                    (filtro, tipo_servicio),
                                    {"viewport": "8,8,12,12",
                                     "location": "1,1",
                                     "ubicacion": u"Direccion",
                                     "tipo": 1},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        # La variable de sesión de búsqueda
        busqueda = {"direccion": u"Direccion",
                    "tipo": TipoServicio.objects.get(id=1),
                    "latitud": "1", "longitud": "1",
                    "filtro": u"puntuacion"}
        self.assertEqual(self.client.session["busqueda"], busqueda)
        # La variable de sesión de resultados
        resultados = Servicio.accepted.filter(
            ubicacion__latitud__range=(8, 12),
            ubicacion__longitud__range=(8, 12),
        )
        self.assertEqual(self._compare_querysets(self.client.session["resultados"], resultados), True)
        # El conjunto de resultados con filtros
        resultados = Servicio.accepted.filter(
            ubicacion__latitud__range=(8, 12),
            ubicacion__longitud__range=(8, 12),
            tipo_servicio__id=1,
        )
        self.assertEqual(self._compare_querysets(response.context["all_results"], resultados), True)

        # Búsqueda para una ubicación específica
        response = self.client.post("/servicios/perfiles/%s/%s/" % \
                                    (filtro, tipo_servicio),
                                    {"viewport": "8,8,12,12",
                                     "location": "1,1",
                                     "ubicacion": u"Direccion"},
                                    HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        # La variable de sesión de búsqueda
        busqueda = {"direccion": u"Direccion",
                    "tipo": None,
                    "latitud": "1", "longitud": "1",
                    "filtro": u"puntuacion"}
        self.assertEqual(self.client.session["busqueda"], busqueda)
        # La variable de sesión de resultados
        resultados = Servicio.accepted.filter(
            ubicacion__latitud__range=(8, 12),
            ubicacion__longitud__range=(8, 12),
        )
        self.assertEqual(self._compare_querysets(self.client.session["resultados"], resultados), True)

        # Búsqueda para la ubicación específica guardada en la sesión y con un
        # tipo de servicio envíado como get
        tipo_servicio = 1
        response = self.client.get("/servicios/perfiles/%s/%s/" % \
                                   (filtro, tipo_servicio),
                                   {},
                                   HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        # La variable de sesión de búsqueda
        busqueda = {"direccion": u"Direccion",
                    "tipo": TipoServicio.objects.get(id=1),
                    "latitud": "1", "longitud": "1",
                    "filtro": "puntuacion"}
        self.assertEqual(self.client.session["busqueda"], busqueda)
        # La variable de sesión de resultados
        resultados = Servicio.accepted.filter(
            ubicacion__latitud__range=(8, 12),
            ubicacion__longitud__range=(8, 12),
        )
        self.assertEqual(self._compare_querysets(self.client.session["resultados"], resultados), True)
        # El conjunto de resultados con filtros
        resultados = Servicio.accepted.filter(
            ubicacion__latitud__range=(8, 12),
            ubicacion__longitud__range=(8, 12),
            tipo_servicio__id=1,
        )
        self.assertEqual(self._compare_querysets(response.context["all_results"], resultados), True)

    def test_responder_opinion(self):
        """
        Responde una opinión por medio de ajax
        """
        (servicio, admin) = self._create_servicio("Nuevo")
        opinion = self._create_opinion(servicio)
        respuesta = "Hola"
        self.client.login(username="Nuevo", password="123")
        response = self.client.get("/servicios/json_responder_opinion/%s/%s/" % \
                                   (opinion.id, respuesta), {},
                                   HTTP_HOST='127.0.0.1:8082')
        self.assertEqual(response.status_code, 200)
        opinion = Opinion.objects.get(id=1)
        self.assertEqual(respuesta, opinion.respuesta.texto)
