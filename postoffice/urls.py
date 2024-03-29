"""postoffice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.contrib import admin
from django.conf import settings
admin.site.site_header = "Postoffice Administration"
admin.site.site_title = "Postoffice Admin Portal"
admin.site.index_title = "Welcome to Postoffice Admin Portal!"
from dns.views import dns_query


urlpatterns = [
    path('dns-query', dns_query.as_view(), name='query_dns'),
    path('dns/', include('dns.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG == True:
    urlpatterns += [
#        path('admin/', admin.site.urls),
    ]
