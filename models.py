from django.db import models
import settings
from datetime import datetime as dtdt
import django.utils.formats as django_format
from django.utils import timezone

def content_file_name(instance, filename):
    ext = '.xlsx'
    if '.' in filename:
        ext = filename[filename.rfind('.'):]
    current_tz = timezone.get_current_timezone()
    now = django_format.date_format(current_tz.localize(dtdt.now()), 'DATETIME_FORMAT') 
    return 'imex_files/imex_%s%s' % (now, ext)

class Process(models.Model):
    action = models.CharField(max_length=2, choices=(
        ('IM', 'Import'),
        ('EX', 'Export')))
    group = models.CharField(max_length=100)
    imex_file = models.FileField(upload_to=content_file_name)
    log = models.TextField(default='')
    errors = models.TextField(null=True, blank=True)
    time_taken = models.FloatField('Time Taken', default = 0, blank=True)
    complete = models.BooleanField(default = False)
    successful = models.BooleanField(default = False)
    time = models.DateTimeField(auto_now_add=True)
    
    def add_line(self, line):
        self.log += line + '\n'
        self.save()    
    
    def delete(self, *args, **kwargs):
        storage, path = None, None
        try:
            storage, path = self.imex_file.storage, self.imex_file.path
        except:
            pass
        super(Process, self).delete(*args, **kwargs)
        if storage and path:
            storage.delete(path)
    
    class Meta:
        verbose_name_plural = 'Processes'
        verbose_name = 'Process'
        ordering = ['id']