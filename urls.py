from django.conf.urls import patterns, url
import Imex.views as views

urlpatterns = patterns('',
    url(r'^$', views.Imex.as_view(), name='imex'),
    url(r'^process/(?P<command>\w+)$', views.Process.as_view(), name='imex_process'),
)