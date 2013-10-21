from django.contrib import admin
import Imex.models as m

class Process(admin.ModelAdmin):
    list_display = ('id', 'time', 'complete', 'successful', 'time_taken', 'action', 'imex_file')

admin.site.register(m.Process, Process)