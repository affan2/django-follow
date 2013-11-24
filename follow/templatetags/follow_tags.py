from django import template
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from follow.models import Follow
from follow import utils
import re

from django.template import loader, RequestContext
from django.conf import settings

register = template.Library()

@register.tag
def follow_url(parser, token):
    """
    Returns either a link to follow or to unfollow.
    
    Usage::
        
        {% follow_url object %}
        {% follow_url object user %}
        
    """
    bits = token.split_contents()
    return FollowLinkNode(*bits[1:])

class FollowLinkNode(template.Node):
    def __init__(self, obj, user=None):
        self.obj = template.Variable(obj)
        self.user = user
        
    def render(self, context):
        obj = self.obj.resolve(context)
        
        if not self.user:
            try:
                user = context['request'].user
            except KeyError:
                raise template.TemplateSyntaxError('There is no request object in the template context.')
        else:
            user = template.Variable(self.user).resolve(context)
        
        return utils.follow_url(user, obj)
        

@register.filter
def is_following(user, obj):
    """
    Returns `True` in case `user` is following `obj`, else `False`
    """
    return Follow.objects.is_following(user, obj)

@register.filter
def followers(user, obj):
    return utils.get_follower_users_for_object(obj)


@register.filter
def follower_count(user, obj):
    return utils.get_follower_count_for_object(obj)

@register.filter
def vendor_following_count(user):
    return utils.get_following_vendors_count_for_user(user)

@register.tag
def follow_form(parser, token):
    """
    Renders the following form. This can optionally take a path to a custom 
    template. 
    
    Usage::
    
        {% follow_form object %}
        {% follow_form object "app/follow_form.html" %}
        
    """
    bits = token.split_contents()
    return FollowFormNode(*bits[1:])

class FollowFormNode(template.Node):
    def __init__(self, obj, tpl=None):
        self.obj = template.Variable(obj)
        self.template = tpl[1:-1] if tpl else 'follow/form.html'
    
    def render(self, context):
        ctx = {'object': self.obj.resolve(context)}
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)

class FollowingList(template.Node):
    def __init__(self, obj):
        self.object = template.Variable(obj)

    def render(self, context):
        obj_instance = self.object.resolve(context)
        content_type = ContentType.objects.get_for_model(obj_instance).pk
        return reverse('get_vendor_followers', kwargs={'content_type_id': content_type, 'object_id': obj_instance.pk })

class AsNode(template.Node):
    """
    Base template Node class for template tags that takes a predefined number
    of arguments, ending in an optional 'as var' section.
    """
    args_count = 3

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse and return a Node.
        """
        bits = token.split_contents()
        args_count = len(bits) - 1
        if args_count >= 2 and bits[-2] == 'as':
            as_var = bits[-1]
            args_count -= 2
        else:
            as_var = None
        if args_count != cls.args_count:
            arg_list = ' '.join(['[arg]' * cls.args_count])
            raise template.TemplateSyntaxError("Accepted formats {%% %(tagname)s "
                "%(args)s %%} or {%% %(tagname)s %(args)s as [var] %%}" %
                {'tagname': bits[0], 'args': arg_list})
        args = [parser.compile_filter(token) for token in
            bits[1:args_count + 1]]
        return cls(args, varname=as_var)

    def __init__(self, args, varname=None):
        self.args = args
        self.varname = varname

    def render(self, context):
        result = self.render_result(context)
        if self.varname is not None:
            context[self.varname] = result
            return ''
        return result

    def render_result(self, context):
        raise NotImplementedError("Must be implemented by a subclass")

class FollowingListSubset(AsNode):

    def render_result(self, context):
        obj_instance = self.args[0].resolve(context)
        sIndex = self.args[1].resolve(context)
        lIndex = self.args[2].resolve(context)
        content_type = ContentType.objects.get_for_model(obj_instance).pk
        
        return reverse('get_vendor_followers_subset', kwargs={
            'content_type_id': content_type, 'object_id': obj_instance.pk, 'sIndex':sIndex, 'lIndex':lIndex})

@register.tag
def vendor_follower_subset_info_url(parser, token):
    bits = token.split_contents()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("Accepted format "
                                  "{% vendor_follower_subset_info_url [actor_instance] %}")
    else:
        return FollowingListSubset.handle_token(parser, token)

@register.tag
def vendor_follower_info_url(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("Accepted format {% vendor_follower_info_url [instance] %}")
    else:
        return FollowingList(*bits[1:])

class UserFollowingVendorsList(template.Node):
    def __init__(self, user):
        self.user = template.Variable(user)

    def render(self, context):
        user_instance = self.user.resolve(context)
        content_type = ContentType.objects.get_for_model(user_instance).pk
        return reverse('get_vendor_following', kwargs={'content_type_id': content_type, 'object_id': user_instance.pk })

class UserFollowingVendorsListSubset(AsNode):

    def render_result(self, context):
        obj_instance = self.args[0].resolve(context)
        sIndex = self.args[1].resolve(context)
        lIndex = self.args[2].resolve(context)
        content_type = ContentType.objects.get_for_model(obj_instance).pk
        
        return reverse('get_vendor_following_subset', kwargs={
            'content_type_id': content_type, 'object_id': obj_instance.pk, 'sIndex':sIndex, 'lIndex':lIndex})

@register.tag
def vendor_following_subset_info_url(parser, token):
    bits = token.split_contents()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("Accepted format "
                                  "{% vendor_following_subset_info_url [actor_instance] %}")
    else:
        return UserFollowingVendorsListSubset.handle_token(parser, token)

@register.simple_tag(takes_context=True)
def render_vendor_following_subset(context, user_obj, sIndex, lIndex, data_chunk=settings.MIN_FOLLOWERS_CHUNK, orientation='horizontal'):
    vendors = utils.get_following_vendors_subset_for_user(user_obj, sIndex, lIndex)
    template_name = 'generic/vendor_list.html'
    search_param = ''

    if orientation == 'vertical':
        template_name = 'generic/vendor_list_v.html'
        search_param = '?v=1'
    template = loader.get_template(template_name)
    content_type = ContentType.objects.get_for_model(user_obj).pk
    data_href = reverse('get_vendor_following_subset', kwargs={ 'content_type_id':content_type,
                                                            'object_id':user_obj.pk,
                                                            'sIndex':sIndex,
                                                            'lIndex':lIndex})
    return template.render(RequestContext(context['request'], {
            "vendors": vendors,
            'is_incremental': False,
            'data_href':data_href + search_param,
            'data_chunk': data_chunk
        }))

@register.tag
def vendor_following_info_url(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("Accepted format {% vendor_following_info_url [instance] %}")
    else:
        return UserFollowingVendorsList(*bits[1:])

@register.filter
def get_class_name(value):
    return value.__class__.__name__