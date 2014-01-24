from django import forms

import Imex.models as m
import Imex.tasks as tasks
import SkeletalDisplay.views_base as viewb
from django.core.urlresolvers import reverse
from django.db import models
import settings

worker_funcs=(('export', 'Generate XLSX Export'),)

class Imex(viewb.TemplateBase):
    template_name = 'imex.html'
    top_active = 'imex'
    side_menu = False
    show_crums = False
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Export'
        self._context['page_menu'] = self.set_links()
        return self._context
    
    def set_links(self):
        links= []
        for func_name, label in worker_funcs:
            links.append({'url': reverse('imex_process', kwargs={'command': func_name}), 'name': label})
        return links

class Process(viewb.TemplateBase):
    template_name = 'process.html'
    top_active = 'imex'
    side_menu = False
    show_crums = False
    
    def get_context_data(self, **kw):
        self._context['expected_ms'] = 0
        self.choose_func(kw)
        return self._context
    
    def set_links(self):
        links= []
        for func_name, label in worker_funcs:
            links.append({'url': reverse('imex_process', kwargs={'command': func_name}), 'name': label})
        return links
        
    def choose_func(self, kw):
        if 'command' in kw:
            command = kw['command']
            if command in [func_name for func_name, _ in worker_funcs]:
                getattr(self, command)()
            else:
                self._context['errors'] = ['No function called %s' % command]
    
    def export(self):
        processor = m.Process.objects.create(action='EX')
        successful = m.Process.objects.filter(complete=True, successful=True, action='EX')
        if successful.exists():
            expected_time = successful.aggregate(expected_time = models.Max('time_taken'))['expected_time']
            self._context['expected_ms'] = '%0.0f' % ((expected_time * 1000) + 1500)
        self._context['media_url'] = settings.MEDIA_URL
        self._context['json_url'] = '%s/%d.json' % (reverse('rest-%s-%s-list' % ('imex', 'Process')), processor.id)
        tasks.perform_export(processor.id)



