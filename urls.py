import os.path
from django.conf.urls.defaults import *
from django.contrib import admin
from forum.views import index
from forum import views as app

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', index),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/content/images/favicon.ico'}),
    (r'^favicon\.gif$', 'django.views.generic.simple.redirect_to', {'url': '/content/images/favicon.gif'}),
    (r'^content/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'templates/content').replace('\\','/')}
    ),
    (r'^account/', include('django_authopenid.urls')),
    url(r'^about/$', app.about, name='about'),
    url(r'^faq/$', app.faq, name='faq'),
    url(r'^logout/$', app.logout, name='logout'),
    url(r'^answers/(?P<id>\d+)/comments/$', app.answer_comments, name='answer_comments'),
    url(r'^answers/(?P<id>\d+)/edit/$', app.edit_answer, name='edit_answer'),
    url(r'^answers/(?P<id>\d+)/revisions/$', app.answer_revisions, name='answer_revisions'),
    url(r'^questions/$', app.questions, name='questions'),
    url(r'^questions/ask/$', app.ask, name='ask'),
    url(r'^questions/unanswered/$', app.unanswered, name='unanswered'),
    url(r'^questions/(?P<id>\d+)/edit/$', app.edit_question, name='edit_question'),
    url(r'^questions/(?P<id>\d+)/close/$', app.close, name='close'),
    url(r'^questions/(?P<id>\d+)/reopen/$', app.reopen, name='reopen'),
    url(r'^questions/(?P<id>\d+)/answer/$', app.answer, name='answer'),
    url(r'^questions/(?P<id>\d+)/vote/$', app.vote, name='vote'),
    url(r'^questions/(?P<id>\d+)/revisions/$', app.question_revisions, name='question_revisions'),
    url(r'^questions/(?P<id>\d+)/comments/$', app.question_comments, name='question_comments'),
    #place general question item in the end of other operations
    url(r'^questions/(?P<id>\d+)//*', app.question, name='question'),
    (r'^tags/$', app.tags),
    (r'^tags/(?P<tag>[^/]+)/$', app.tag),
    (r'^users/$',app.users),
    (r'^users/(?P<user_id>\d+)/recent//*', app.user_recent),
    (r'^users/(?P<user_id>\d+)/responses//*', app.user_responses),
    (r'^users/(?P<user_id>\d+)/reputation//*', app.user_reputation_history),
    (r'^users/(?P<user_id>\d+)/favorites//*', app.users_favorites),
    url(r'^users/(?P<user_id>\d+)//*', app.user_stats, name='user'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^nimda/(.*)', admin.site.root),
)
