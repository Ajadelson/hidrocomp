"""hidrocomp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from data.views import atualiza_pelo_hidroweb,cria_posto,series,serie,posto,postos#,cria_serie_extensa
from ecohydro.views import seleciona_posto,seleciona_dados_posto

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^atualizar/', atualizar_banco),
    #url(r'^', series,name="series"),
    
    #url(r'^atualizar/file/$', cria_serie_extensa,name="cria_serie_extensa"),
    url(r'^atualizar/web/$', atualiza_pelo_hidroweb,name="atualiza_pelo_hidroweb"),
    url(r'^postos/novo/$', cria_posto,name="cria_posto"),
    url(r'^postos/seleciona/$', seleciona_posto,name="seleciona_posto"),
    url(r'^posto/(?P<posto_id>\d+)/seleciona_dados/$', seleciona_dados_posto,name="seleciona_dados_posto"),
    #url(r'^$', series,name="series"),

    url(r'^posto/(?P<posto_id>\d+)$', posto,name="posto"),
    url(r'^postos/$', postos,name="postos"),
    url(r'^$', postos,name="postos"),
    ##url(r'^serie/(?P<serie_id>\d+)/$', serie,name="serie"),
    
]