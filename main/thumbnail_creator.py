import os
from django.core.files.base import ContentFile
from django.core.files import File
from django.contrib.contenttypes.models import ContentType
import threading
from Queue import Queue, Empty
from django.conf import settings
from PIL import Image

THREADS_PER_SERVER = 32

from threading import Lock
print_lock = Lock()
error_log = open('thumb_errors.log', 'w')

def create_thumb_for_field(instance, field):
    file_field = getattr(instance, field)
    try:
        file = open(settings.MEDIA_ROOT+file_field.name)
    except IOError:
        print "file not found %s" % (settings.MEDIA_ROOT+file_field.name)
        return 
    file = File(file)
    num_instances = 0
    #file = getattr(instance, self.field)
    if not file:
        print "(%d/%d) ID: %d -- Skipped -- No file" % (
            0,
            num_instances,
            instance.id)
        return
    file_name = os.path.basename(file.name)
    
    
    # Keep them informed on the progress.
    print "(%d/%d) ID: %d -- %s" % (0, num_instances,
                                    instance.id, file_name)
    
    try:
        fdat = file.read()
    except IOError:
        # Key didn't exist.
        print "(%d/%d) ID %d -- Skipped -- File missing on NFS" % (
            0,
            num_instances,
            instance.id)
        return

    try:
        file_contents = ContentFile(fdat)
    except ValueError:
        # This field has no file associated with it, skip it.
        print "(%d/%d) ID %d --  Skipped -- No file on field)" % (
            0,
            num_instances,
            instance.id)
        return
    
    
    # obtian the source image
    image = Image.open(file_contents)
    # Convert to RGBA (alpha) if necessary
    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGBA')
        
    # Saving pumps it back through the thumbnailer, if this is a
    # ThumbnailField. If not, it's still pretty harmless.
    for thumb in file_field.field.thumbs:
        thumb_name, thumb_options = thumb
        # Pre-create all of the thumbnail sizes.
        print "creating %s for %s" % (thumb_name, file_name)
        file_field.create_and_store_thumb(image, thumb_name, thumb_options)
        
class ThumbnailCreatorThread(threading.Thread):

    def __init__(self, parent, to_do_queue):
        super(ThumbnailCreatorThread, self).__init__()
        self.parent = parent
        self.to_do_queue = to_do_queue
        
    def run(self):
        shoud_continue = True
        while self.parent.NOT_FINISHED:
            while not self.to_do_queue.empty():
                data = self.to_do_queue.get(timeout=4)
                try:
                    print "called with %s %s" % (data['instance'],
                                                 data['field'])
                    create_thumb_for_field(data['instance'], data['field'])
                except:
                    with print_lock:
                        error_log.write(
                            "model:{0} instance_pk:{1} field:{2}\n".format(
                            data['instance'].__class__,
                            data['instance'].pk,
                            data['field']))
                    continue
                
                


class RegenerateThumbs():
    def __init__(self, queryset, field_name):
        self.to_do = Queue(maxsize=40)
        self.instances = queryset
        self.field_name = field_name
        self.num_instances = self.instances.count()
        self.NOT_FINISHED = True

    def start(self):
        # Filenames are keys in here, to help avoid re-genning something that
        # we have already done.
        tasks = []
        for worker in xrange(0, THREADS_PER_SERVER):
            task = ThumbnailCreatorThread(self, self.to_do)
            task.start()
            tasks.append(task)
            
        for instance in self.instances.iterator():
            self.to_do.put({'instance': instance, 'field': self.field_name})
            self.NOT_FINISHED = False

        for task in tasks:
            task.join()
    
