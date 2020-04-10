from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
# Create your views here.

class ip_address(View):
    @staticmethod
    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    def get(self, request, *args, **kwargs):
        ip = self.get_ip(request)
        response = HttpResponse(f'{ip}', content_type="text/plain")
        response['ip'] = ip
        return response
