import celery
import openpyxl
from django.core.files import File
import SkeletalDisplay
import time
import Imex.ImportExport as imex
import Imex.models
import traceback

@celery.task
def perform_export(processor_id):
    delete_old_processes(processor_id)
    processors = Imex.models.Process.objects.filter(id=processor_id)
    if not processors.exists():
        msg = 'Processor id=%d' % processor_id
        print msg
        return msg
    processor = processors[0]
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

def perform_import(fname, delete_first):
    context={}
    logger = SkeletalDisplay.Logger()
    try:
        if delete_first:
            pass
#             SalesEstimates.worker.delete_before_upload(logger.addline)
        imex.ReadXl(fname, logger.addline)
    except Exception, e:
        context['errors'] = ['ERROR: %s' % str(e)]
    else:
        context['success'] = ['Document Successfully Uploaded']
    finally:
        context['info'] = logger.get_log()
    return context

def delete_old_processes(pid):
    for p in Imex.models.Process.objects.filter(id__lt=pid - 1):
        p.delete()



