from django.conf.urls import patterns, url
import Imex.views as views

urlpatterns = patterns('',
    url(r'^export$', views.Export.as_view(), name='imex_export'),
    url(r'^import$', views.Import.as_view(), name='imex_import'),
    url(r'^process/(?P<command>\w+)$', views.Process.as_view(), name='imex_process'),
    url(r'^process/(?P<command>\w+)/(?P<group>\w+)$', views.Process.as_view(), name='imex_process'),
)