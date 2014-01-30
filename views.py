from django import forms

import Imex.models as m
import Imex.tasks as tasks
import SkeletalDisplay.views_base as viewb
from django.core.urlresolvers import reverse
from django.db import models
import settings
from django.shortcuts import redirect

actions = (('imex_export', 'Generate XLSX Export'), ('imex_import', None),)

class Export(viewb.TemplateBase):
    template_name = 'export.html'
    top_active = 'imex_export'
    side_menu = False
    show_crums = False
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Export'
        self._context['page_menu'] = self.set_links()
        return self._context
    
    def set_links(self):
        links= []
        for func_name, label in actions:
            if label:
                links.append({'url': reverse('imex_process', kwargs={'command': func_name}), 'name': label})
        return links

class ExcelUploadForm(forms.Form):
    xlfile = forms.FileField(
        label='Select Excel (xlsx) File to Upload',
        help_text='should be in standard format for this system'
    )

class Import(viewb.TemplateBase):
    template_name = 'import.html'
    top_active = 'imex_import'
    side_menu = False
    show_crums = False
    
    def get_context_data(self, **kw):
        self._context['title'] = 'Import'
        self._context['process_url'] =  reverse('imex_process', kwargs={'command': 'imex_import'})
        self._context['upload_form'] =  ExcelUploadForm()
        
        if 'errors' in self.request.session:
            self._context['errors'] = self.request.session['errors']
        return self._context

class Process(viewb.TemplateBase):
    template_name = 'process.html'
    side_menu = False
    show_crums = False
    _redirect = None
    
    def get(self, request, *args, **kw):
        if 'top_active' in request.session:
            self.top_active = request.session['top_active']
        return super(Process, self).get(request, *args, **kw)
    
    def post(self, request, *args, **kw):
        page = self.get(request, *args, **kw)
        if self._redirect:
            return self._redirect
        return page
    
    _act_map = {'imex_export': 'EX', 'imex_import':'IM'}
    def get_context_data(self, **kw):
        self._context['expected_ms'] = 0
        if 'command' in kw and kw['command'] in self._act_map:
            act = self._act_map[kw['command']]
            self._context['act'] = act
            prev_successful = m.Process.objects.filter(complete=True, successful=True, action=act)
            if prev_successful.exists():
                print 'average_of %s' % ','.join([ '%0.3f' % p.time_taken for p in prev_successful])
                expected_time = prev_successful.aggregate(expected_time = models.Avg('time_taken'))['expected_time']
                self._context['expected_ms'] = '%0.0f' % (expected_time * 1000)
        success = self.choose_func(kw)
        if not success:
            return self._context
        self._context['media_url'] = settings.MEDIA_URL
        self._context['json_url'] = '%s/%d.json' % (reverse('rest-imex-Process-list'), self._pid)
        return self._context
        
    def choose_func(self, kw):
        if 'command' in kw:
            command = kw['command']
            if command in [func_name for func_name, _ in actions]:
                return getattr(self, command)()
            else:
                self._context['errors'] = ['No function called %s' % command]
    
    def imex_export(self):
        processor = m.Process.objects.create(action='EX')
        self._pid = processor.id
        tasks.perform_export(self._pid)
        return True
    
    def imex_import(self):
        error = None
        if self.request.method != 'POST':
            error = "No post data"
        else:
            form = ExcelUploadForm(self.request.POST, self.request.FILES)
            if  not form.is_valid():
                error = "Form not valid"
            elif not str(self.request.FILES['xlfile']).endswith('.xlsx'):
                error = 'File must be xlsx, not xls or any other format.'
        if error:
            print 'refused'
            self.request.session['errors'] = [error]
            self._redirect = redirect(reverse('imex_import'))
            return
        p = m.Process.objects.create(action='IM', imex_file = self.request.FILES['xlfile'])
        msg = tasks.perform_import(p.id)
        if msg:
            self._context['errors'].append(msg)
        self._pid = p.id
        return True



