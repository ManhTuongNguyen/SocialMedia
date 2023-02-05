from django import template
from django.template.defaultfilters import stringfilter

from core.models import LikePost, CustomName, Post, Profile, Comment

register = template.Library()


register.filter(is_safe=True)
def is_liked_post(value, arg):
    if arg is None:
        return False
    # value = Post, arg = username
    try:
        temp = LikePost.objects.get(post=value, username=arg)
        return temp is not None
    except:
        return False

@register.filter(is_safe=True)
@stringfilter
def get_custom_name_post(value):
    # value = Post
    post = Post.objects.get(id=value)
    try:
        custom_name = CustomName.objects.get(user=post.user).fullname
        return custom_name
    except:
        return post.user


@register.filter(is_safe=True)
@stringfilter
def get_custom_name_profile(value):
    # value = Profile
    try:
        custom_name = CustomName.objects.get(user=value).fullname
        return custom_name
    except:
        return value


@register.filter(is_safe=True)
@stringfilter
def get_custom_name_comment(value):
    # value = Comment
    try:
        username = Comment.objects.get(id=value).user
        custom_name = CustomName.objects.get(user=username).fullname
        return custom_name
    except:
        return username


@register.filter(is_safe=True)
def get_comment(value):
    # value = post
    try:
        comment = Comment.objects.filter(post=value).order_by("-created")[:2]
        return reversed(comment)
    except:
        return None


@register.filter(is_safe=True)
def is_youtube_link(value):
    # value = post caption
    caption = str(value)
    if caption.__contains__("https://www.youtube.com/") or caption.__contains__("https://youtu.be"):
        return True
    return False


@register.filter(is_safe=True)
@stringfilter
def get_youtube_id(value):
    # value = post caption
    # https://youtu.be/RkqeD5ZzkF8?list=RDRkqeD5ZzkF8
    # https://youtu.be/jJPMnTXl63E
    # https://www.youtube.com/watch?v=jJPMnTXl63E
    youtube_link = str(value)
    if youtube_link.__contains__('youtu.be'):
        temp = youtube_link.split('/')
        len_temp = len(temp)
        return temp[len_temp - 1][:11]
    if youtube_link.__contains__("youtube.com/watch?"):
        temp = youtube_link.split("=")
        len_temp = len(temp)
        return temp[len_temp - 1][:11]


register.filter('is_liked_post', is_liked_post)
register.filter('get_custom_name_post', get_custom_name_post)
register.filter('get_custom_name_profile', get_custom_name_profile)
register.filter('get_custom_name_comment', get_custom_name_comment)
register.filter('get_comment', get_comment)
register.filter('is_youtube_link', is_youtube_link)
register.filter('get_youtube_id', get_youtube_id)
