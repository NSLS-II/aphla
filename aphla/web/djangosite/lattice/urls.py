from django.conf.urls import patterns, url

from lattice import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^download$', views.download, name='download'),
    url(r'^contact$', views.contact, name='contact'),
)
