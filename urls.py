import os.path
from django.conf.urls.defaults import *
from django.contrib import admin
from forum.views import index
from forum import views as app

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', index),
    (r'^content/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'templates/content').replace('\\','/')}
    ),
    (r'^account/', include('django_authopenid.urls')),
    (r'^questions/$', app.questions),
    (r'^questions/ask/$', app.ask),
    (r'^questions/unanswered/$', app.unanswered),
    url(r'^questions/(?P<id>\d+)/answer/$', app.answer, name='answer'),
    #place general question item in the end of other operations
    url(r'^questions/(?P<id>\d+)//*', app.question, name='question'),
    (r'^tags/$', app.tags),
    (r'^tags/(?P<tag>[^/]+)/$', app.tag),
    (r'^users/$',app.users),
    (r'^users/(?P<user_id>\d+)/(?P<username>\w+)$', app.user_stats),
    (r'^users_recent/(?P<user_id>\d+)/(?P<username>\w+)$', app.user_recent),
    (r'^users_responses/(?P<user_id>\d+)/(?P<username>\w+)$', app.user_responses),
    (r'^users_reputation_history/(?P<user_id>\d+)/(?P<username>\w+)$', app.user_reputation_history),
    (r'^users_favorites/(?P<user_id>\d+)/(?P<username>\w+)$', app.users_favorites),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/(.*)', admin.site.root),
)
