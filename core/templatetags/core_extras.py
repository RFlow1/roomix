from django import template
register = template.Library()

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr, False)

@register.filter
def add_class(field, css_class):
    """Inject CSS classes onto any Django form field widget."""
    return field.as_widget(attrs={'class': css_class})