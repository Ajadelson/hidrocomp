import logging
from numpy import nan,mean
import pandas as pd
from datetime import datetime
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from data.models import Posto,SerieOriginal,Variavel,Reducao,SerieTemporal,Discretizacao,SerieReduzida#,NivelConsistencia,Unidade
from .ecohidro import EstatisticaBasica, MediaMovel, RazaoMudanca
from .forms import FormSelecionaPosto,FormDadosPosto
from plotly.offline import plot
from plotly.graph_objs import Scatter, Figure, Layout




logging.basicConfig(filename="Logs.log",level=logging.INFO)



def visualiza_data_por_discretizacao(data,discretizacao):
    try:
        int(discretizacao)
        return data.year
    except:
        if discretizacao=="M":
            return "%i/%i"%(data.month,data.year)
        else:
            return "%i/%i/%i"%(data.day,data.month,data.year)

def seleciona_posto(request):
    postos = ((posto.id,posto.nome) for posto in Posto.objects.all())
    if request.method == 'POST':
        form = FormSelecionaPosto(postos=postos,data=request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            posto_id = dados['posto']
            #posto = Posto.objects.get(id=posto_id)
            url = "/posto/%s/seleciona_dados"%posto_id
            print(url)
            return HttpResponseRedirect(url)
    return render(request,'seleciona_posto.html',{'aba':'postos','form':FormSelecionaPosto(postos=postos)})

def seleciona_dados_posto(request,posto_id):
    data = datetime.now()
    posto = Posto.objects.get(id=int(posto_id))
    ecohidro = EstatisticaBasica(posto)
    #a = RazaoMudanca(posto)
    #original = a.pegar_serie_original(1,10)
    #reduzida = a.obter_series_reduzidas()
    #resultado = a.prepara_serie_reduzida()
    #print(resultado)
    if request.method == 'GET':
        #Solicitação inicial para visualização do formulário
        print(datetime.now())
        return render(request,'seleciona_dados_posto.html',{'aba':'postos','form':FormDadosPosto(variaveis=list(ecohidro.variaveis))})
    if request.method == 'POST':
        #Se o usuário enviou uma solicitação pelo formulário
        form = FormDadosPosto(data=request.POST,variaveis=list(ecohidro.variaveis))
        if form.is_valid():
            #Se o formulário for válido
            dados = form.cleaned_data
            #Salvando solicitação do usuário em um arquivo .log
            logging.info("$ Selecionado pelo usuario: variável: %i; discretização: %s; reducao: %i"%(
                int(dados['variavel']),                                                                                        dados['discretizacao'], 
                int(dados['reducao'])))
            #obtem a série original
            if int(dados['reducao'])==9999:
                ecohidro = MediaMovel(posto)
                ecohidro.atualiza_informacoes(dados['tipo_media_movel'],int(dados['discretizacao_media_movel']))
            else:                              
                ecohidro = EstatisticaBasica(posto) 
                ecohidro.atualiza_informacoes(dados['discretizacao'],int(dados['reducao']))
            t = int(dados['variavel'])
            original = ecohidro.pegar_serie_original(t)
            #Verifica se já existem séries reduzidas
            reduzida = ecohidro.obter_series_reduzidas()
            if reduzida:
                #No caso em que a solicitação já exista no banco de dados, não é necessário processar os dados novamente
                resultado = SerieTemporal.objects.filter(Id=reduzida[0].serie_temporal_id)
                ecohidro.serie_reduzida = reduzida[0]
            else:
                #prepara a série reduzida
                resultado = ecohidro.prepara_serie_reduzida()
            print("Tempode execução: " + str(datetime.now()-data))
            a = plot({
                'data':[Scatter(x=[d.data_e_hora for d in resultado], y=[d.dado for d in resultado]),],
                'layout':Layout(title=str(ecohidro.serie_reduzida),xaxis={'title':'tempo'},yaxis={'title':"%s (%s)"
                                                                                  %(str(ecohidro.serie_reduzida.serie_original.variavel),
                                                                                    str(ecohidro.serie_reduzida.serie_original.unidade))})
            
            },auto_open=False, output_type='div')
            resultado = [(visualiza_data_por_discretizacao(d.data_e_hora,dados['discretizacao']),d.dado,) for d in resultado]
            print(resultado)
            return render(request,'seleciona_dados_posto.html',{'aba':'postos','form':form,'dados':resultado,'grafico':a})
    
'''
#IMPORTAR ISSO:

import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab as plt
from PIL import Image
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

#CRIAR ESTAFUNÇÃO
def cria_imagens():
    buffer1 = HttpResponse(content_type = "image/png")
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    graphIMG = Image.frombytes("RGB",canvas.get_width_height(),canvas.tostring_rgb())
    canvas.close_event()
    graphIMG.save(buffer1,"PNG")
    graphIMG.close()
    plt.close()
    plt.clf()
    plt.cla()
    
    return buffer1
    
def filtra_temporais_por_originais(originais):
    queries = [Q(Id=o.serie_temporal_id) for o in originais]
    query = queries.pop()
    for item in queries:
        query |= item
    return query
'''


    