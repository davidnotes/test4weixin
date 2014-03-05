from django.conf.urls import patterns, include, url
from test4weixin.views import handleRequest

urlpatterns = patterns('',
    url(r'^$', handleRequest),
)
