from django.urls import include, re_path

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = ('',
    # Examples:
    # re_path(r'^$', 'project.views.home', name='home'),
    # re_path(r'^project/', include('project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # re_path(r'^admin/', include(admin.site.urls)),
    re_path('^', include('follow.urls')),
    re_path('^$', 'app.views.index')
)
