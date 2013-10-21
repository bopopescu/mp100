"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth import login        
from MP100.fotos import models
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


class newHome(BaseOperations):
    def test_userLogin(self):
        """
        validates that the user login form in the new Home page works.
        """
        from django.core.urlresolvers import reverse
        from forms import SignupForm
        #crea un usuario
        user = self._create_user(self._get_random_string(5))
    
        #logea al usuario 'user'
        response = self.client.post(reverse('new_main_portal'),
                                    {'email':user.email, 
                                     'password':'123', 
                                     'login':'Login'},
                                    HTTP_HOST='127.0.0.1:8082')

        #verifica que el usuario esta logeado
        self.assertEqual(self.client.session.get('_auth_user_id'),
                         user.id,
                         'Login procces in new home failed')
            

