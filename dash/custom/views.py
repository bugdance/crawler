# # # @@ Import current path
import sys
sys.path.append('..')


from django.shortcuts import render

from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework import viewsets



# Create your views here.

def OverView(request):
    return render(request, 'layui/overview.html')

def IndustryView(request):
    return render(request, 'layui/industry.html')

def PlatformView(request):
    return render(request, 'layui/platform.html')

def MediumView(request):
    return render(request, 'layui/medium.html')


    
    
# class OverView(APIView):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse(content=open("./template/layui/overview.html", encoding='UTF-8').read())


# class IndustryView(APIView):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse(content=open("./template/layui/industry.html", encoding='UTF-8').read())


# class PlatformView(APIView):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse(content=open("./template/layui/platform.html", encoding='UTF-8').read())


# class MediumView(APIView):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse(content=open("./template/layui/medium.html", encoding='UTF-8').read())