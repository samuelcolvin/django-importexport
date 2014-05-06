import openpyxl, time, settings
from django.core.files import File
import HotDjango
import Imex.ImportExport as imex
import Imex.models
import traceback
import threading

# it's assumed that if celery is installed it's running unless celery_available is set to False
CELERY_AVAILABLE = False
if CELERY_AVAILABLE:
    try:
        import celery
    except ImportError:
        CELERY_AVAILABLE = False
        if settings.DEBUG:
            print 'Celery is not available, running imex using threading'
    else:
        @celery.task
        def _perform_export_celery(processor_id):
            return _perform_export(processor_id)
        @celery.task
        def _perform_import_celery(processor_id):
            return _perform_import(processor_id)


def perform_export(processor_id):
    if CELERY_AVAILABLE:
        return _perform_export_celery.delay(processor_id)
    else:
        t = threading.Thread(target=_perform_export, args = (processor_id,))
        t.start()

def _perform_export(processor_id):
    processor, msg = get_processor(processor_id)
    if not processor:
        return msg
    t = time.time()
    try:
        writer = imex.WriteXl(processor.add_line, processor.group)
    except imex.KnownError, e:
        processor.errors = 'ERROR: %s' % str(e)
    except Exception:
        processor.errors = traceback.format_exc()
    else:
        f_tmp = open(writer.fname, 'r')
        processor.imex_file.save(writer.fname, File(f_tmp))
        processor.time_taken = time.time() - t
        processor.successful = True
    finally:
        processor.complete = True
        processor.save()

def perform_import(processor_id):
    if CELERY_AVAILABLE:
        return _perform_import_celery.delay(processor_id)
    else:
        t = threading.Thread(target=_perform_import, args = (processor_id,))
        t.start()

def _perform_import(processor_id):
    processor, msg = get_processor(processor_id)
    if not processor:
        return msg
    t = time.time()
    try:
        imex.ReadXl(processor.imex_file.path, processor.add_line, processor.group)
    except Exception, e:
        processor.errors = 'ERROR: %s' % str(e)
    else:
        processor.time_taken = time.time() - t
        processor.successful = True
    finally:
        processor.complete = True
        processor.save()

def delete_old_processes(action):
    for p in Imex.models.Process.objects.filter(action=action).order_by('-id')[5:]:
        p.delete()

def get_processor(processor_id):
    processors = Imex.models.Process.objects.filter(id=processor_id)
    if not processors.exists():
        msg = 'Processor id=%d does not exist' % processor_id
        print msg
        return None, msg
    else:
        delete_old_processes(processors[0].action)
    return processors[0], None

