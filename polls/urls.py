from django.conf.urls import include, url
from polls import views
from django.views.generic import TemplateView
from django.urls import path

urlpatterns = [
    path(r'', TemplateView.as_view(template_name="homepage.html")),
    path(r'add/', views.new_poll, name='new_poll'),
    url(r'^answer/(?P<uid>[0-9]+)/(?P<qid>[0-9]+)/(?P<token>[0-9A-Za-z_-]+)/$',
        views.collect_answer, name='answer'),
    url(r'^vote/(?P<uid>[0-9]+)/(?P<qid>[0-9]+)/(?P<token>[0-9A-Za-z_-]+)/$',
        views.collect_vote, name='vote'),
    url(r'success/', TemplateView.as_view(template_name="success.html")),
    url(r'error/', TemplateView.as_view(template_name="error.html")),
]