from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='toggle'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='follow'),
    url(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='unfollow'),
    url(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/follower/$', 'follow.views.get_vendor_followers', name='get_vendor_followers'),
	url(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/following/$', 'follow.views.get_vendor_following', name='get_vendor_following'),
    url(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/followers/range/(?P<sIndex>\d+)/(?P<lIndex>\d+)/$',
        'follow.views.get_vendor_followers_subset', name='get_vendor_followers_subset'),
    url(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/following/range/(?P<sIndex>\d+)/(?P<lIndex>\d+)/$',
        'follow.views.get_vendor_following_subset', name='get_vendor_following_subset'),
)
