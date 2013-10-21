import logging
import lockfile
import datetime
import itertools
import random

from django.core.management import base
from optparse import make_option
from django.conf import settings

logger = logging.getLogger('djangoproject.main.commands.main_create_thumbnails')

class Command(base.NoArgsCommand):
    option_list = base.NoArgsCommand.option_list + (
        make_option('-s', action='store_true', dest='silentmode',
            default=False, help='Run in silent mode'),
        make_option('--debug', action='store_true',
            dest='debugmode', default=False,
            help='Debug mode (overrides silent mode)'),
    )

    def handle_noargs(self, **options):
        if not options['silentmode']:
            logging.getLogger('djangoproject').setLevel(logging.INFO)
        if options['debugmode']:
            logging.getLogger('djangoproject').setLevel(logging.DEBUG)

        if 1:
            lock = lockfile.FileLock('/tmp/main_create_thumbnails')
            logger.info("aquiring lock")
            lock.acquire(10)
            with lock:
                logger.info("got lock")
                from main.thumbnail_creator import RegenerateThumbs
                from fotos.models import UserProfile
                logger.info("creating thumbs for UserProfile Avatar")
                r = RegenerateThumbs(UserProfile.objects.all(),
                                                                'foto')
                r.start()
                #from generic_images.models import AttachedImage
                #logger.info("creating thumbs for AttachedImage image")
                #r = RegenerateThumbs(AttachedImage.objects.all(), 'image')
                #r.start()
                #from audio_video.models import Video
                #logger.info("creating thumbs for Video splash_image")
                #r = RegenerateThumbs(AttachedImage.objects.all(),
                #                     'splash_image')
                #r.start()
