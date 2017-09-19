import copy

from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse
from yingun.utils.page import PageInfo
from yingun.utils.filter_code import FilterList


class BaseYinGunAdmin(object):

    list_display = "__all__"

    action_list = []

    filter_list = []

    add_or_edit_model_form = None

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site
        self.request = None
        self.app_lable = model_class._meta.app_label
        self.model_name = model_class._meta.model_name

    def get_add_or_edit_model_form(self):
        if self.add_or_edit_model_form:
            return self.add_or_edit_model_form
        else:
            from django.forms import ModelForm
            class MyModelForm(ModelForm):
                class Meta:
                    model = self.model_class
                    fields = "__all__"
            return MyModelForm

    @property
    def urls(self):
        from django.conf.urls import url
        info = self.model_class._meta.app_label, self.model_class._meta.model_name

        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(.+)/delete/$', self.delete_view, name='%s_%s_delete' % info),
            url(r'^(.+)/change/$', self.change_view, name='%s_%s_change' % info),
        ]
        return urlpatterns

    def changelist_view(self,request):

        ###### 增加按钮
        from django.http.request import QueryDict   # request.GET 是 QueryDict 的对象
        param_dict = QueryDict(mutable=True)        #创建QueryDict对象, 加上mutable=True参数后,可以修改内部元素
        if request.GET:
            param_dict['_changelistfilter'] = request.GET.urlencode()

        base_add_url = reverse("{2}:{0}_{1}_add".format(self.app_lable,self.model_name,self.site.namespace))
        add_url = "{0}?{1}".format(base_add_url,param_dict.urlencode())

        self.request = request

        ############### 分页

        base_page_url = reverse("{2}:{0}_{1}_changelist".format(self.app_lable, self.model_name, self.site.namespace))
        page_param_dict = copy.deepcopy(request.GET)
        page_param_dict._mutable = True

        condition = {}


        # 总页数
        all_count = self.model_class.objects.filter(**condition).count()

        # 用户当前想要访问的页码
        current_page = request.GET.get("page")
        page_info = PageInfo(current_page, all_count,base_page_url,page_param_dict,3)

        result_list = self.model_class.objects.filter(**condition)[page_info.start():page_info.end()]

        ########### action操作
        # get请求,显示下拉框

        action_list = []
        for item in self.action_list:
            tpl = {'name':item.__name__,'text':item.text}
            action_list.append(tpl)

        if request.method == 'POST':
            func_name_str = request.POST.get('action')
            ret = getattr(self,func_name_str)(request)
            action_page_url = reverse(
                "{2}:{0}_{1}_changelist".format(self.app_lable, self.model_name, self.site.namespace))
            if ret:
                action_page_url = "{0}?{1}".format(action_page_url,request.GET.urlencode())

            return redirect(action_page_url)

        ###########组合搜索操作

        from django.db.models.fields.related import ForeignKey,ManyToManyField,OneToOneField
        filter_list = []

        for option in self.filter_list:
            if option.is_func:
                data_list = option.field_or_func(self,request)
            else:
                filed = self.model_class._meta.get_field(option.field_or_func)
                if isinstance(filed,OneToOneField):
                    pass
                elif isinstance(filed,ManyToManyField):
                    data_list = FilterList(option,filed.rel.model.objects.all(),request.GET)
                elif isinstance(filed,ForeignKey):
                    data_list = FilterList(option,filed.rel.model.objects.all(),request.GET)
                else:
                    data_list = FilterList(option,filed.model.objects.all(),request.GET)
            filter_list.append(data_list)












        context = {
            'result_list':result_list,
            'list_display':self.list_display,
            'ygadmin_obj':self,
            'add_url':add_url,
            "page_info": page_info,
            "action_list":action_list,
            "filter_list":filter_list
        }

        return render(request, 'yg/change_list.html',context)

    def add_view(self,request):
        if request.method == "GET":
            model_form_obj = self.get_add_or_edit_model_form()()
            context = {
                'form': model_form_obj
            }
            return render(request, 'yg/add.html', context)
        else:
            model_form_obj = self.get_add_or_edit_model_form()(data=request.POST,files=request.FILES)
            if model_form_obj.is_valid():
                obj = model_form_obj.save()
                popid = request.GET.get('popup')
                if popid:

                    print(obj.pk)
                    print(str(obj))
                    print(popid)
                    return render(request,"yg/popup_response.html",{'data_dict': {'pk': obj.pk, 'text': str(obj), 'popid': popid}})
                    # return render(request,"yg/popup_response.html",{"data_dict":{"pk":obj.pk,"text":str(obj),"popid":popid}})

                else:
                    base_list_url = reverse("{2}:{0}_{1}_changelist".format(self.app_lable, self.model_name, self.site.namespace))
                    list_url = "{0}?{1}".format(base_list_url,request.GET.get('_changelistfilter') )
                    print(list_url)
                    return redirect(list_url)

            context = {
                'form':model_form_obj
            }

            return render(request,'yg/add.html',context)

    def delete_view(self,request,pk):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name
        data = '%s_%s_delete' % info
        return HttpResponse(data)

    def change_view(self,request,pk):

        # 1. 获取_changelistfilter中传递的参数
            # request.GET.get("_changelistfilter")
        # 2. 页面显示并提供默认值
        # 3. 返回页面

        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse("ID 不存在")

        if request.method == "GET":
            model_form_obj = self.get_add_or_edit_model_form()(instance=obj)
        else:
            print("111")
            model_form_obj = self.get_add_or_edit_model_form()(data=request.POST,files=request.FILES,instance=obj)
            if model_form_obj.is_valid():
                model_form_obj.save()
                base_list_url = reverse(
                    "{2}:{0}_{1}_changelist".format(self.app_lable, self.model_name, self.site.namespace))
                list_url = "{0}?{1}".format(base_list_url, request.GET.get('_changelistfilter'))
                #print(list_url)
                return redirect(list_url)
        context = {
            'form':model_form_obj
        }


        return render(request,"yg/edit.html",context)



class YinGunSite(object):
    def __init__(self):
        self._registry = {}
        self.namespace = "yingun"
        self.app_name = "yingun"


    def register(self,model_class,xxxxx = BaseYinGunAdmin):
        self._registry[model_class] = xxxxx(model_class,self)
    """
    {
        UserInfo类 : BaseYinGunAdmin(UserInfo类,YinGunSite对象)
        Role类 : BaseYinGunAdmin(Role类,YinGunSite对象)
        XX类 : BaseYinGunAdmin(XX类,YinGunSite对象)
    }

    """


    def get_urls(self):
        from django.conf.urls import url,include
        ret = [
            #url(r'^login/',self.login,name='login'),
            #url(r'^logout/',self.logout,name='logout'),
        ]


        for model_cls,yingun_admin_obj in self._registry.items():

            app_label = model_cls._meta.app_label
            model_name = model_cls._meta.model_name

            #print(app_label,model_name)

            ret.append(url(r'^%s/%s/' % (app_label,model_name), include(yingun_admin_obj.urls)))


        return ret


    @property
    def urls(self):

        return self.get_urls(),self.app_name,self.namespace

    def login(self,request):
        return HttpResponse('login')

    def logout(self,request):
        return HttpResponse('logout')



site = YinGunSite()