from django.shortcuts import render,HttpResponse
from django.urls import reverse
# Create your views here.

from app01 import models


def test(request):
    user_group_list = models.UserGroup.objects.all()

    return render(request,'test.html',{'user_group_list':user_group_list})

def add_test(request):
    if request.method == "GET":
        return render(request,'add_test.html')
    else:
        popid = request.GET.get('popup')
        if popid:
            # 通过popup新创建了一个页面进来
            title = request.POST.get('title')
            obj = models.UserGroup.objects.create(title=title)
            # response = {'id':obj.id,'title': obj.title}
            # 1. 关闭popup页面
            # 2. 将新增的数据添加，传送到原来发送pop页面中的ugID标签位置 popid = ugID
            return render(request,'popup_response.html',{'id':obj.id,'title':obj.title,'popid':popid })
        else:
            title = request.POST.get('title')
            models.UserGroup.objects.create(title=title)
            return HttpResponse('重定向列表页面：所有用户组')