from django.conf.urls import include, url
from django.contrib import admin
from .views import HomeView, PostDataView, get_file

urlpatterns = [
    # Examples:
    # url(r'^$', 'website.views.home', name='home'),

    url(r'^the_mp3$', get_file),
    url(r'^api/brain-data$', PostDataView.as_view()),
    url(r'^', HomeView.as_view()),

    url(r'^admin/', include(admin.site.urls)),
]
