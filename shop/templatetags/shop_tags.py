from django import template
from django.urls import translate_url


register = template.Library()


@register.filter
def switch_language_for_current_url(request_path, to_lang):
    return translate_url(request_path, to_lang)
