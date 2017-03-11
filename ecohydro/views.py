import pandas as pd
from django.shortcuts import render
from django.http import HttpResponseRedirect
from data.models import Posto,SerieOriginal,Variavel,Reducao,SerieTemporal,Discretizacao#,NivelConsistencia,Unidade,SerieReduzida
from .forms import FormSelecionaPosto,FormDadosPosto
from numpy import nan,mean
from django.db.models import Q
# import the logging library
import logging
logging.basicConfig(filename="Logs.log",level=logging.INFO)

# Get an instance of a logger

'''
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
'''
funcoes_reducao = {'máxima':max,'mínima':min,'soma':sum, 'média':mean}
meses = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}


def filtra_temporais_por_originais(originais):
    queries = [Q(Id=o.serie_temporal_id) for o in originais]
    query = queries.pop()
    for item in queries:
        query |= item
    return query

def get_id():
    if SerieOriginal.objects.count()>0:
        o = [o.serie_temporal_id for o in SerieOriginal.objects.all()]
        r = [o.serie_temporal_id for o in SerieReduzida.objects.all()]
        j = max(o.extend(r))+1 if r else o
    else:
        j=1

def dados_diarios_pandas(dados_temporais,obs):
    #dados_temporais = [d for d in dados_temporais if d.data_e_hora.year ==1982]
    consistidos = sorted([d for d in dados_temporais if obs[d.Id]==2],key=lambda x:x.data_e_hora)
    dados_temporais = consistidos if consistidos else dados_temporais
    dados = [o.dado if not o is None else nan for o in dados_temporais]
    datas = [o.data_e_hora for o in dados_temporais]
    #niveis = [obs[o.Id] for o in dados_temporais]
    #print(niveis)
    #d=pd.date_range(start=min(datas),end=max(datas))
    #print(d)
    pf = pd.DataFrame({"dado" : dados}, index=pd.DatetimeIndex(datas))
    gp = pd.Grouper(freq='D',sort=True)
    pfgp = pf.groupby(gp).mean()
    return pfgp

def sugere_mes_inicio_ano_hidrologico(df):
    medias_por_mes = df["dado"].groupby(pd.Grouper(freq='M')).mean()
    minimas_dos_anos = df.groupby(pd.Grouper(freq='AS')).idxmin()
    return pd.value_counts([d.month for d in minimas_dos_anos["dado"]]).idxmax()
    
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

def dicionario_de_anos_hidrologicos(df):
    nmes = sugere_mes_inicio_ano_hidrologico(df)
    gp = df["dado"].groupby(pd.Grouper(freq="AS-%s"%meses[nmes]))
    dic = dict(list(gp))
    anos_hidrologicos = {key.year:dic[key] for key in dic.keys()}
    return anos_hidrologicos

def seleciona_dados_posto(request,posto_id):
    posto = Posto.objects.get(id=int(posto_id))
    originais = SerieOriginal.objects.filter(posto=posto)
    variaveis_disponiveis = [o.variavel for o in originais]
    variaveis =((variavel.id,variavel.variavel) for variavel in [v for v in Variavel.objects.all() if v in variaveis_disponiveis])
    if request.method == 'GET':
        temporais = SerieTemporal.objects.filter(filtra_temporais_por_originais(originais))
        return render(request,'seleciona_dados_posto.html',{'aba':'postos','form':FormDadosPosto(variaveis=list(variaveis))})
    if request.method == 'POST':
        form = FormDadosPosto(data=request.POST,variaveis=list(variaveis))
        if form.is_valid():
            dados = form.cleaned_data
            variavel=Variavel.objects.get(id=int(dados['variavel']))
            originais = SerieOriginal.objects.filter(posto=posto,variavel=variavel)
            obs = {o.serie_temporal_id:o.tipo_dado.id for o in originais}
            temporais = SerieTemporal.objects.filter(filtra_temporais_por_originais(originais))
            diarios = dados_diarios_pandas(temporais,obs)
            médias_móveis_por_dia = diarios.rolling(window=30,center=False).mean()
            anos_hidrologicos = dicionario_de_anos_hidrologicos(médias_móveis_por_dia)
            medias_moveis = {key:anos_hidrologicos[key].min() for key in anos_hidrologicos.keys()}  
            print(medias_moveis)
            #serie = pd.DataFrame({'dados':list(anos_hidrologicos.values())},index=list(anos_hidrologicos.keys()))
            
            #discretizacao = Discretizacao.objects.get(codigo_pandas=dados['discretizacao'])
            #reducao = Reducao.objects.get(id=int(dados['reducao']))
            
            
            
            
            #print(pd.rolling_mean(pf, window=30, center=False))
            #print(pd.rolling_mean(pf, window=30, center=False))
            #gp = pd.Grouper(freq=discretizacao.codigo_pandas)
            
            #dic = dict([gp])
            '''
            
            #
            #.agg(funcoes_reducao[reducao.tipo])
            
            
            '''
            return render(request,'seleciona_dados_posto.html',{'aba':'postos','form':form})
    
#LOGGING: http://james.lin.net.nz/2012/09/19/creating-custom-log-handler-that-logs-to-database-models-in-django/
    


    