from django.urls import re_path

from coconuts import views

urlpatterns = [
    # backend
    re_path(r"^images/contents/(?P<path>.*)$", views.content_list),
    re_path(r"^images/download/(?P<path>.*)$", views.download),
    re_path(r"^images/render/(?P<path>.*)$", views.render_file),
    # frontend
    re_path(r"^(?P<path>.*)$", views.browse),
]
