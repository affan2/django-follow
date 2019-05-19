from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import post_save, post_delete
from .registry import model_map
from .signals import followed, unfollowed
import inspect


class FollowManager(models.Manager):
    def fname(self, model_or_obj_or_qs):
        """ 
        Return the field name on the :class:`Follow` model for ``model_or_obj_or_qs``.
        """
        if isinstance(model_or_obj_or_qs, QuerySet):
            _, fname = model_map[model_or_obj_or_qs.model]
        else:
            cls = model_or_obj_or_qs if inspect.isclass(model_or_obj_or_qs) else model_or_obj_or_qs.__class__
            _, fname = model_map[cls]
        return fname

    def create(self, user, obj, **kwargs):
        """
        Create a new follow link between a user and an object
        of a registered model type.
        
        """
        follow = Follow(user=user)
        follow.target = obj
        follow.site=Site.objects.get_current()
        follow.save()
        return follow

    def get_or_create(self, user, obj, **kwargs):
        """ 
        Almost the same as `FollowManager.objects.create` - behaves the same 
        as the normal `get_or_create` methods in django though. 

        Returns a tuple with the `Follow` and either `True` or `False`

        """
        if not self.is_following(user, obj):
            return self.create(user, obj, **kwargs), True
        return self.get_follows(obj).get(user=user), False

    def is_following(self, user, obj):
        """ Returns `True` or `False` """
        if isinstance(user, AnonymousUser):
            return False
        return 0 < self.get_follows(obj).filter(user=user).count()

    def get_follows(self, model_or_obj_or_qs):
        """
        Returns all the Follow objects associated with a certain model, object or queryset..
        """
        from people.models import PeopleWhiteLabel, UserProfile
        people = None
        if settings.SITE_ID > 1:
            white_label_people = PeopleWhiteLabel.objects.filter(
                site_id=settings.SITE_ID
            ).values_list(
                'id',
                flat=True
            )
            people = UserProfile.objects.filter(
                white_label_site__in=white_label_people
            ).values_list(
                'user',
                flat=True
            )

        fname = self.fname(model_or_obj_or_qs)
        if isinstance(model_or_obj_or_qs, QuerySet):
            return self.filter(**{'%s__in' % fname: model_or_obj_or_qs})

        if inspect.isclass(model_or_obj_or_qs):
            return self.exclude(**{fname:None})

        if people:
            return self.filter(**{fname:model_or_obj_or_qs}).filter(
                user__in=people,
                site_id=settings.SITE_ID
            )
        return self.filter(**{fname:model_or_obj_or_qs}).filter(site_id=settings.SITE_ID)

    def get_follows_subset(self, model_or_obj_or_qs, sIndex, lIndex):
        """
        Returns all the Follow objects associated with a certain model, object or queryset..
        """
        fname = self.fname(model_or_obj_or_qs)

        if isinstance(model_or_obj_or_qs, QuerySet):
            return self.filter(**{'%s__in' % fname: model_or_obj_or_qs})[sIndex:lIndex]

        if inspect.isclass(model_or_obj_or_qs):
            return self.exclude(**{fname:None})[sIndex:lIndex]

        return self.filter(**{fname:model_or_obj_or_qs})[sIndex:lIndex]


class Follow(models.Model):
    """
    This model allows a user to follow any kind of object. The followed
    object is accessible through `Follow.target`.
    """
    user = models.ForeignKey(User, related_name='following')

    site = models.ForeignKey(Site, default=settings.SITE_ID,
        verbose_name='site')

    datetime = models.DateTimeField(auto_now_add=True)

    objects = FollowManager()

    def __str__(self):
        return u'%s' % self.target

    def _get_target(self):
        for Model, (_, fname) in model_map.iteritems():
            try:
                if hasattr(self, fname) and getattr(self, fname):
                    return getattr(self, fname)
            except Model.DoesNotExist:
                # In case the target was deleted in the previous transaction
                # it's already gone from the db and this throws DoesNotExist.
                return None

    def _set_target(self, obj):
        for _, fname in model_map.values():
            setattr(self, fname, None)
        if obj is None:
            return
        _, fname = model_map[obj.__class__]
        setattr(self, fname, obj)

    target = property(fget=_get_target, fset=_set_target)


def follow_dispatch(sender, instance, created=False, **kwargs):
    if created:
        followed.send(instance.target.__class__, user=instance.user, target=instance.target, instance=instance)


def unfollow_dispatch(sender, instance, **kwargs):
    # FIXME: When deleting out of the admin, django *leaves* the transaction
    # management after the user is deleted and then starts deleting all the
    # associated objects. This breaks the unfollow signal. Looking up
    # `instance.user` will throw a `DoesNotExist` exception.  The offending
    # code is in django/db/models/deletion.py#70
    # At least that's what the error report looks like and I'm a bit short
    # on time to investigate properly.
    # Unfollow handlers should be aware that both target and user can be `None`
    try:
        user = instance.user
    except User.DoesNotExist:
        user = None

    unfollowed.send(instance.target.__class__, user=user, target=instance.target, instance=instance)


post_save.connect(follow_dispatch, dispatch_uid='follow.follow_dispatch', sender=Follow)
post_delete.connect(unfollow_dispatch, dispatch_uid='follow.unfollow_dispatch', sender=Follow)
