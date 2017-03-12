from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404
import matplotlib
matplotlib.use('Agg')
#from matplotlib import pylab as plt
#from PIL import Image

#import numpy
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
#from numpy import arange
from .forms import FormCriaSerieDeDados,FormCriaPosto

#from matplotlib import pylab as plt
#from PIL import Image

from .models import SerieOriginal,SerieTemporal,Posto,Variavel,NivelConsistencia,Unidade,Discretizacao,TipoPosto,Localizacao,Fonte

import pandas as pd
from django.contrib import messages

from .le_dados import Hidroweb,ONS


            
            
    

    
def series(request):
    series=SerieOriginal.objects.all()
    return render(request,'series.html',{'series':series,'aba':'series'})

def serie(request,serie_id):
    serie = get_object_or_404(SerieOriginal, pk=serie_id)
    dados = SerieTemporal.objects.filter(id=serie_id)
    return render(request,'serie.html',{'serie':serie,'dados':dados,'aba':'series'})

def posto(request,posto_id):
    posto = get_object_or_404(Posto, pk=posto_id)
    series = SerieOriginal.objects.filter(posto=posto)
    return render(request,'posto.html',{'posto':posto,'series':series,'aba':'postos'})

def postos(request):
    postos=Posto.objects.all()
    return render(request,'postos.html',{'postos':postos,'aba':'postos'})

def cria_serie_extensa(request):
    if request.method == 'POST':
        form = FormCriaSerieDeDados(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            print(request.FILES['arquivo'].name)
            return HttpResponse("ok")
    form =FormCriaSerieDeDados
    return render(request,'carrega_serie_de_dados.html',{'aba':'nova','form':FormCriaSerieDeDados})

@login_required
def atualiza_pelo_hidroweb(request):
    if request.method == 'POST':
        form = FormCriaSerieDeDados(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            estacoes = [dados["posto"],]
            
            hid = Hidroweb(estacoes,dados["tipo_de_dado"],request)
            #original = SerieOriginal.objects.create()
            executa = hid.executar()
            if executa:
                messages.add_message(request, messages.SUCCESS, '%s'%executa)
                return render(request,'carrega_serie_de_dados.html',{'aba':'nova','form':form})
            messages.add_message(request, messages.SUCCESS, 'Concluído!')
            return render(request,'carrega_serie_de_dados.html',{'aba':'nova'})
    form =FormCriaSerieDeDados
    return render(request,'carrega_serie_de_dados.html',{'aba':'nova','form':form})

@login_required
def cria_posto(request):
    if request.method == 'POST':
        form = FormCriaPosto(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            tipo_posto = TipoPosto.objects.get(id=dados["tipo_posto"])
            fonte = Fonte.objects.get(id=dados["fonte"])
            if fonte.tipo == "ONS":
                ons = ONS()
                ons.executa()
            codigo_ana = dados["codigo_ana"]
            #nome = dados["nome"]
            localizacao = Localizacao.objects.get(id=1)
            postos = Posto.objects.filter(codigo_ana=codigo_ana)
            hid = Hidroweb(codigo_ana,8,request)
            if postos:
                messages.add_message(request, messages.ERROR, 'O posto de código %s já existe no sistema.'%postos[0].codigo_ana)
            else:
                nome = hid.obtem_nome_posto()
                posto = Posto.objects.create(tipo_posto=tipo_posto,fonte=fonte,codigo_ana=codigo_ana,nome=nome, localizacao=localizacao)
                posto.save()
            for codigo_variavel in range(8,10):
                hid.codigo_variavel = codigo_variavel
                #original = SerieOriginal.objects.create()
                executa = hid.executar()
                if executa:
                    messages.add_message(request, messages.SUCCESS, '%s'%executa) 
            messages.add_message(request, messages.SUCCESS, 'Concluído!')
            return render(request,'cria_posto.html',{'aba':'nova'})    
    form =FormCriaPosto
    return render(request,'cria_posto.html',{'aba':'nova','form':form})





'''
def gantt(request):
    plt.clf()
    plt.cla()
    dados_temporais=Serie_Temporal.objects.filter(Serie_Temporal_id=2)
    lista=lista_anos_disponiveis(dados_temporais)
    print(lista)
    anos=[dado[0] for dado in lista]
    dados=[[dado[1],0,1,dado[1],0] for dado in lista]
    matrix = numpy.matrix(dados)
    labels=['43200000','43203485','78500000','43484400','43159800']
    plota_matriz(matrix,labels)
    return cria_imagens()
    
    #plt.title("Diagrama de Gantt")
    
    #Respondendo o gráfico em uma solicitação http:
    




def plota_matriz(matriz,lista_postos):
    
    fig = plt.figure(figsize=(12,7))
    ax = fig.add_subplot(1,4,2)
    #ax.set_aspect('equal')

    plt.imshow(matriz, interpolation='nearest', cmap=plt.cm.binary)

    ax.set_xticklabels(lista_postos)

    ax.xaxis.tick_top()
    locs, lista_postos = plt.xticks()
    plt.setp(lista_postos, rotation=90)
    
    plt.axhline(y=9.5, xmin=0, xmax=1, hold=None)
    #plt.axhline(y=19.5, xmin=0, xmax=1, hold=None)

    start, end = ax.get_xlim()
    
    ax.xaxis.set_ticks(range(int(start), int(end)+1, 1))
    ax.yaxis.set_ticks(arange(10, -1, -10))
    
    #ax.set_ylim((10.5,-0.5))
    
    #ax.set_yticklabels([2016, 2015,2014,2013,2012,2011,2010,2009,2008,2007,2006])
    
    #plt.gca().tight_layout()


    #start, end = ax.get_ylim()
    #ax.yaxis.set_
    
def gera_curva_chave(request,posto_id):
    posto = get_object_or_404(Posto, pk=posto_id)
    series=Serie_Original.objects.filter(posto=posto)
    #s = dict(series[0])
    print(series[0].__dict__)
    niveis=set([e.Tipo_Dado_ for e in series])
    cores=["r","b"]
    j=0
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    maior_serie=0
    for i in (niveis):
        serie_vazao_id=[e.serie_Temporal_id for e in series if e.Tipo_Dado_==i and e.Variavel_=="Vazão"][0]
        serie_cota_id=[e.serie_Temporal_id for e in series if e.Tipo_Dado_==i and e.Variavel_=="Cota"][0]
        vazoes=Serie_Temporal.objects.filter(Serie_Temporal_id=serie_vazao_id)
        cotas=Serie_Temporal.objects.filter(Serie_Temporal_id=serie_cota_id)
        curva_chave(vazoes,cotas,i,cores[j],ax1)
        if len(vazoes)>maior_serie:
            maior_serie=len(vazoes)
        print("ok")
        j+=1
    plt.title('Curva-Chave - Est. %s'%posto.codigo_ana if posto.codigo_ana else 'N/A')
    ax1.legend(loc='upper right')
    plt.xlabel('Vazão (m³/s)')
    plt.ylabel('h (cm)')
    plt.xlim((0,max([v.Dado for v in vazoes])+1))
    return cria_imagens()
        
def gera_maior_curva_chave(request,posto_id):
    posto = get_object_or_404(Posto, pk=posto_id)
    series=Serie_Original.objects.filter(posto=posto)
    niveis=set([e.Tipo_Dado_ for e in series])
    cores=["r","b"]
    j=0
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    maior_serie=0
    for i in (niveis):
        serie_vazao_id=[e.serie_Temporal_id for e in series if e.Tipo_Dado_==i and e.Variavel_=="Vazão"][0]
        serie_cota_id=[e.serie_Temporal_id for e in series if e.Tipo_Dado_==i and e.Variavel_=="Cota"][0]
        vazoes=Serie_Temporal.objects.filter(Serie_Temporal_id=serie_vazao_id)
        cotas=Serie_Temporal.objects.filter(Serie_Temporal_id=serie_cota_id)
        curva_chave(vazoes,cotas,i,cores[j],ax1)
        if len(vazoes)>maior_serie:
            maior_serie=len(vazoes)
        print("ok")
        j+=1
    plt.title('Curva-Chave - Est. %s'%posto.codigo_ana if posto.codigo_ana else 'N/A')
    ax1.legend(loc='upper right')
    plt.xlabel('Vazão (m³/s)')
    plt.ylabel('h (cm)')
    plt.xlim((0,max([v.Dado for v in vazoes])+1))
    return cria_imagens()
'''




















