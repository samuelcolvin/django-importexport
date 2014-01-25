import openpyxl
from django.core.files import File
import SkeletalDisplay
import time
import Imex.ImportExport as imex
import Imex.models
import traceback

# it's assumed that if celery is installed it's running unless celery_available is set to False
CELERY_AVAILABLE = True
if CELERY_AVAILABLE:
    try:
        import celery
    except ImportError:
        CELERY_AVAILABLE = False
        print 'Celery is not available, running imex directly'
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
        return _perform_export(processor_id)

def _perform_export(processor_id):
    processor, msg = get_processor(processor_id)
    if not processor:
        return msg
    t = time.time()
    try:
        writer = imex.WriteXl(processor.add_line)
    except Exception, e:
        processor.errors = 'ERROR: %s' % str(e)
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
        return _perform_import(processor_id)

def _perform_import(processor_id):
    processor, msg = get_processor(processor_id)
    if not processor:
        return msg
    t = time.time()
    try:
        imex.ReadXl(processor.imex_file.path, processor.add_line)
    except Exception, e:
        processor.errors = 'ERROR: %s' % str(e)
    else:
        processor.time_taken = time.time() - t
        processor.successful = True
    finally:
        processor.complete = True
        processor.save()

def delete_old_processes(pid):
    for p in Imex.models.Process.objects.filter(id__lt=pid - 1):
        p.delete()

def get_processor(processor_id):
    delete_old_processes(processor_id)
    processors = Imex.models.Process.objects.filter(id=processor_id)
    if not processors.exists():
        msg = 'Processor id=%d does not exist' % processor_id
        print msg
        return None, msg
    return processors[0], None

