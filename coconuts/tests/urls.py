from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # accounts
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', ),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # folders
    url(r'', include('coconuts.urls')),
)
