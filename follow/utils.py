from django.urls import reverse
from django.db.models.fields.related import ManyToManyField, ForeignKey
from .models import Follow
from .registry import registry, model_map
from actstream.models import Action
from actstream.views import actions
from django.conf import settings
from django.db import models


def get_followers_for_object(instance):
    """
    Returns all the Follow objects associated with a certain model, object or queryset..
    """
    return Follow.objects.get_follows(instance)


def get_following_vendors_for_user(user, target_field=None):
    """
    Returns all the users who follow objects associated with a certain model, object or queryset.
    """
    vendors = []
    exclude = {}
    if target_field:
        exclude = {'%s__isnull' % target_field: True}
    followObjects = Follow.objects.all().filter(
        user=user,
        site_id=settings.SITE_ID
    ).exclude(**exclude)
    for followObject in followObjects:
        if followObject.target is not None:
            vendors.append(followObject.target)

    return vendors


def get_following_vendors_subset_for_user(user, sIndex, lIndex):
    """
    Returns all the users who follow objects associated with a certain model, object or queryset.
    """
    vendors = []
    followObjects = Follow.objects.all().filter(user=user, target_blogpost__in=blog.models.BlogPost.objects.published())[sIndex:lIndex]
    for followObject in followObjects:
        if isinstance(followObject._get_target(), blog.models.BlogPost):
            if followObject._get_target() is not None:
                vendors.append(followObject._get_target())

    return vendors


def get_follower_users_for_object(instance):
    """
    Returns all the users who follow objects associated with a certain model, object or queryset.
    """
    followers = []
    followObjects = Follow.objects.get_follows(instance)
    for followObject in followObjects:
        if followObject.user is not None:
            followers.append(followObject.user)
    return followers


def get_follower_users_subset_for_vendor(instance, sIndex, lIndex):
    """
    Returns all the users who follow objects associated with a certain model, object or queryset.
    """
    followers = []
    followObjects = Follow.objects.get_follows_subset(instance, sIndex, lIndex)
    for followObject in followObjects:
        if followObject.user is not None:
            followers.append(followObject.user)
    return followers


def get_follower_count_for_object(instance):
    """
    Returns number of all the users who follow objects associated with a certain model, object or queryset..
    """
    return Follow.objects.get_follows(instance).count()


def get_following_vendors_count_for_user(user):
    """
    Returns all the Follow objects associated with a user.
    """
    return Follow.objects.all().filter(user=user, target_blogpost__in=blog.models.BlogPost.objects.published()).count()


def register(model, field_name=None, related_name=None, lookup_method_name='get_follows'):
    """
    This registers any model class to be follow-able.

    """
    if model in registry:
        return

    registry.append(model)

    if not field_name:
        field_name = 'target_%s' % model.Meta.__module__

    if not related_name:
        related_name = 'follow_%s' % model.Meta.__module__

    field = ForeignKey(model, related_name=related_name, null=True,
        blank=True, db_index=True, on_delete=models.CASCADE, )

    field.contribute_to_class(Follow, field_name)
    setattr(model, lookup_method_name, get_followers_for_object)
    model_map[model] = [related_name, field_name]


def follow(user, obj):
    """ Make a user follow an object """
    actions.follow(user, obj, actor_only=False)
    follow, created = Follow.objects.get_or_create(user, obj)
    return follow


def unfollow(user, obj):
    """ Make a user un-follow an object """
    from django.contrib.contenttypes.models import ContentType
    # from actstream.models import Action
    try:
        actions.unfollow(user, obj)
        follow = Follow.objects.get_follows(obj).filter(user=user)
        follow.delete()
        ctype = ContentType.objects.get_for_model(user)
        target_content_type = ContentType.objects.get_for_model(obj)
        Action.objects.all().filter(
            actor_content_type=ctype,
            actor_object_id=user.id,
            verb=settings.FOLLOW_VERB,
            target_content_type=target_content_type,
            target_object_id=obj.id,
            site_id=settings.SITE_ID
        ).delete()
        return obj
    except Follow.DoesNotExist:
        pass


def toggle(user, obj):
    """ Toggles a follow status. Useful function if you don't want to perform follow
    checks but just toggle it on / off. """
    if Follow.objects.is_following(user, obj):
        return unfollow(user, obj)
    return follow(user, obj)


def follow_link(object):
    return reverse('follow.views.toggle', args=[object._meta.app_label, object._meta.object_name.lower(), object.pk])


def unfollow_link(object):
    return reverse('follow.views.toggle', args=[object._meta.app_label, object._meta.object_name.lower(), object.pk])


def toggle_link(object):
    return reverse('follow.views.toggle', args=[object._meta.app_label, object._meta.object_name.lower(), object.pk])


def follow_url(user, obj):
    """ Returns the right follow/unfollow url """
    return toggle_link(obj)

