from django.template import Library
from types import FunctionType
from django.utils.safestring import mark_safe


register = Library()


def table_body(result_list,list_display,ygadmin_obj):
    # v = []
    # for row in result_list:
    #     sub = []
    #     for name in list_display:
    #         val = getattr(row, name)
    #         sub.append(val)
    #     yield sub
    for row in result_list:
        if list_display == '__all__':
            yield [str(row),]
        else:
        #yield [getattr(row,name) for name in list_display]
            yield [ name(ygadmin_obj,obj=row) if isinstance(name,FunctionType) else getattr(row,name) for name in list_display]

def table_head(list_display,ygadmin_obj):
    if list_display == '__all__':
        yield "对象列表"
    else:
        for item in list_display:
            if isinstance(item, FunctionType):
                yield item(ygadmin_obj, is_header=True)
            else:
                yield ygadmin_obj.model_class._meta.get_field(item).verbose_name

@register.inclusion_tag("yg/md.html")
def func(result_list,list_display,ygadmin_obj):

    v = table_body(result_list,list_display,ygadmin_obj)

    h = table_head(list_display,ygadmin_obj)

    # v = [
    #     ['1','于浩',18],
    #     ['2','淫棍',18]
    # ]

    return {'xxxxx':v,"header_list":h}