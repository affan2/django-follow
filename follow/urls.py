from django.conf.urls.defaults import *
from django.urls import re_path

urlpatterns = ('',
    re_path(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='toggle'),
    re_path(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='follow'),
    re_path(r'^toggle/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/$', 'follow.views.toggle', name='unfollow'),
    re_path(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/follower/$', 'follow.views.get_vendor_followers', name='get_vendor_followers'),
	re_path(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/following/$', 'follow.views.get_vendor_following', name='get_vendor_following'),
    re_path(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/followers/range/(?P<sIndex>\d+)/(?P<lIndex>\d+)/$',
        'follow.views.get_vendor_followers_subset', name='get_vendor_followers_subset'),
    re_path(r'^store/(?P<content_type_id>\d+)/(?P<object_id>\d+)/following/range/(?P<sIndex>\d+)/(?P<lIndex>\d+)/$',
        'follow.views.get_vendor_following_subset', name='get_vendor_following_subset'),
)
