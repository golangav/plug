from django.shortcuts import render,HttpResponse
from django.urls import reverse
# Create your views here.



def test(request):

    url = reverse('yingun:app01_userinfo_add')
    print(url)
    return HttpResponse("...")