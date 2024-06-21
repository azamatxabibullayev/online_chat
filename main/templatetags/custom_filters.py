from django import template
import mimetypes

register = template.Library()


@register.filter(name='is_image')
def is_image(file_url):
    mime_type, encoding = mimetypes.guess_type(file_url)
    return mime_type and mime_type.startswith('image')


@register.filter(name='is_video')
def is_video(file_url):
    mime_type, encoding = mimetypes.guess_type(file_url)
    return mime_type and mime_type.startswith('video')


@register.filter(name='is_audio')
def is_audio(file_url):
    mime_type, encoding = mimetypes.guess_type(file_url)
    return mime_type and mime_type.startswith('audio')
