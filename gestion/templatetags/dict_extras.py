# gestion/templatetags/dict_extras.py

from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    """
    Permite acceder a d[key] en templates:
    {{ dict|get_item:"clave" }}
    """
    if isinstance(d, dict):
        return d.get(key)
    return None
