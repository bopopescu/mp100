"""
 Command for backup database
"""

import os, popen2, time
from django.core.management.base import BaseCommand
from distutils.dir_util import copy_tree

class Command(BaseCommand):
    help = "Backup database. Only Mysql and Postgresql engines are implemented"

    def handle(self, *args, **options):
        from django.db import connection
        from django.conf import settings

        self.engine = settings.DATABASES['default']['ENGINE']
        self.db = settings.DATABASES['default']['NAME']
        self.user = settings.DATABASES['default']['USER']
        self.passwd = settings.DATABASES['default']['PASSWORD']
        self.host = settings.DATABASES['default']['HOST']
        self.port = settings.DATABASES['default']['PORT']        
        
        backup_dir = os.path.join(settings.BASEDIR, 'backups/%s' % time.strftime('fecha_%Y-%m-%d_hora_%H-%M-%S'))
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        outfile = os.path.join(backup_dir, 'backup_%s.sql' % time.strftime('%Y-%m-%d_%H-%M-%S'))
        
        #aqui hace el backup de las imagenes de los usuarios del perfil, fotos del concurso#
        #y fotos del blog#
        perfil_path = os.path.join(settings.MEDIA_ROOT, settings.USERPROFILE_PHOTO_PATH)
        if os.path.exists(perfil_path):    
            copy_tree( perfil_path , os.path.join(backup_dir, 'perfil/') )
            
        fotos_concurso_path = os.path.join(settings.MEDIA_ROOT, settings.USERPHOTOS_FOLDER_PATH)
        if os.path.exists(fotos_concurso_path):
            copy_tree( fotos_concurso_path , os.path.join(backup_dir, 'fotos_concurso'))
            
        fotos_zinnia_path = os.path.join(settings.MEDIA_ROOT, 'uploads/')
        if os.path.exists(fotos_zinnia_path):
            copy_tree( fotos_zinnia_path , os.path.join(backup_dir, 'uploads'))        
        ###########################################################################
        
            
        if self.engine == 'django.db.backends.mysql':
            print 'Doing Mysql backup to database %s into %s' % (self.db, outfile)
            self.do_mysql_backup(outfile)
        elif self.engine in ('django.db.backends.postgresql_psycopg2', 'django.db.backends.postgresql'):
            print 'Doing Postgresql backup to database %s into %s' % (self.db, outfile)
            self.do_postgresql_backup(outfile)
        else:
            print 'Backup in %s engine not implemented' % self.engine

    def do_mysql_backup(self, outfile):
        args = []
        if self.user:
            args += ["--user=%s" % self.user]
        if self.passwd:
            args += ["--password=%s" % self.passwd]
        if self.host:
            args += ["--host=%s" % self.host]
        if self.port:
            args += ["--port=%s" % self.port]
        args += [self.db]

        #con esto funciona en windows con xamp
        os.system('C:/xampp/mysql/bin/mysqldump %s > %s' % (' '.join(args), outfile))
        #con esto funciona en linux
        #os.system('mysqldump %s > %s' % (' '.join(args), outfile))

    def do_postgresql_backup(self, outfile):
        args = []
        if self.user:
            args += ["--username=%s" % self.user]
        if self.passwd:
            args += ["--password"]
        if self.host:
            args += ["--host=%s" % self.host]
        if self.port:
            args += ["--port=%s" % self.port]
        if self.db:
            args += [self.db]
        pipe = popen2.Popen4('pg_dump %s > %s' % (' '.join(args), outfile))
        if self.passwd:
            pipe.tochild.write('%s\n' % self.passwd)
            pipe.tochild.close()