from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag
def query_string_set(request, **kwargs):
    query_dict = QueryDict(request.GET.urlencode(), mutable=True)
    for key, value in kwargs.items():
        query_dict[key] = value
    return query_dict.urlencode()


@register.simple_tag
def query_string_order_by_toggle(request, field):
    query_dict = QueryDict(request.GET.urlencode(), mutable=True)
    order_by = query_dict.get('order_by', None)
    if field == order_by:
        order_by = f'-{field}'
    else:
        order_by = field
    query_dict['order_by'] = order_by
    return query_dict.urlencode()


@register.simple_tag
def query_string_list_toggle(request, key, value):
    query_dict = QueryDict(request.GET.urlencode(), mutable=True)
    lst = query_dict.getlist(key, [])
    if value in lst:
        lst.remove(value)
    else:
        lst.append(value)
    query_dict.setlist(key, lst)
    return query_dict.urlencode()
