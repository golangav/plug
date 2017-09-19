import copy
from types import FunctionType
from django.utils.safestring import mark_safe
class FilterOption(object):
    def __init__(self, field_or_func, is_multi=False, text_func_name=None, val_func_name=None):
        """
        :param field: 字段名称或函数
        :param is_multi: 是否支持多选
        :param text_func_name: 在Model中定义函数，显示文本名称，默认使用 str(对象)
        :param val_func_name:  在Model中定义函数，显示文本名称，默认使用 对象.pk
        """
        self.field_or_func = field_or_func
        self.is_multi = is_multi
        self.text_func_name = text_func_name
        self.val_func_name = val_func_name

    @property
    def is_func(self):
        if isinstance(self.field_or_func, FunctionType):
            return True

    @property
    def name(self):
        if self.is_func:
            return self.field_or_func.__name__
        else:
            return self.field_or_func


class FilterList(object):
    def __init__(self,option,queryset,request):
        self.option = option
        self.queryset = queryset
        self.param_dict = copy.deepcopy(request.GET)
        self.path_info = request.path_info

    def __iter__(self):
        from django.http.request import QueryDict
        # /arya/app01/userinfo/?mm=2&fk=2&fk=21&username=大刘
        # self.param_dict = {'id': ['666'], 'page': ['1'], 'name': ['fangshaowei']}
        # /arya/app01/userinfo/?mm=2&fk=2&fk=21

        yield mark_safe("<div class='all-area'>")
        if self.option.name in self.param_dict:
            pop_val = self.param_dict.pop(self.option.name) # [1,] 1
            url = "{0}?{1}".format(self.path_info, self.param_dict.urlencode())
            # self.param_dict[self.option.name] = pop_val
            self.param_dict.setlist(self.option.name,pop_val)
            yield mark_safe("<a href='{0}'>全部</a>".format(url))
        else:
            url = "{0}?{1}".format(self.path_info,self.param_dict.urlencode())
            yield mark_safe("<a class='active' href='{0}'>全部</a>".format(url))
        yield mark_safe("</div><div class='others-area'>")


        for row in self.queryset:
            param_dict = copy.deepcopy(self.param_dict)
            val = str(getattr(row,self.option.val_func_name)() if self.option.val_func_name else row.pk)
            text = getattr(row,self.option.text_func_name)() if self.option.text_func_name else str(row)
            # self.param_dict   --->  username=fangshaowei&ug=1&email=666
            # {'username': ['fangshaowei'], 'ug': ['1'], 'email': ['666']
            active = False
            if self.option.is_multi:
                value_list = param_dict.getlist(self.option.name)
                if val in value_list:
                    value_list.remove(val)
                    active = True
                else:
                    param_dict.appendlist(self.option.name,val)

            else:
                value_list = param_dict.getlist(self.option.name)
                if val in value_list:
                    active = True
                param_dict[self.option.name] = val

            url = "{0}?{1}".format(self.path_info,param_dict.urlencode())
            if active:
                tpl = "<a class='active' href='{0}'>{1}</a>".format(url,text)
            else:
                tpl = "<a href='{0}'>{1}</a>".format(url, text)
            yield mark_safe(tpl)


        yield mark_safe("</div>")