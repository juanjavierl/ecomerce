import re
from django import template
from django.utils.html import urlize
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def urlize_mode(text, args="ver_mas,br"):
    """
    Filtro personalizado:
    - ver_mas: convierte URLs en 'Ver más' con target="_blank'
    - ocultar: elimina las URLs del texto
    - default: usa urlize normal

    Extra:
    - br: respeta saltos de línea con <br>
    - nobr: ignora saltos de línea
    """
    if not text:
        return ""

    # separar argumentos
    parts = args.split(",")
    mode = parts[0].strip() if parts else "ver_mas"
    linebreaks = "br" in parts  # si incluye "br" activamos saltos de línea

    url_pattern = r'(https?://[^\s]+)'

    if mode == "ver_mas":
        def replace_url(match):
            url = match.group(0)
            return f'<a href="{url}" target="_blank">Ver más</a>'
        new_text = re.sub(url_pattern, replace_url, text)

    elif mode == "ocultar":
        new_text = re.sub(url_pattern, '', text).strip()

    else:
        new_text = urlize(text, nofollow=True, autoescape=True)

    # aplicar saltos de línea solo si se pide
    if linebreaks:
        new_text = new_text.replace("\n", "<br>")

    return mark_safe(new_text)

@register.filter
def get_attr(obj, attr_name):
    attr = getattr(obj, attr_name, None)
    # Si es callable (método sin parámetros), lo ejecutamos
    if callable(attr):
        return attr()
    return attr

@register.filter
def boolean_si_no(value):
    if value is True or str(value).lower() == "true":
        return "Sí"
    elif value is False or str(value).lower() == "false":
        return "No"
    return value  # si no es boolean, devuelve tal cual
