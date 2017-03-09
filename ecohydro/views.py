import pandas as pd
from django.shortcuts import render
from django.http import HttpResponseRedirect
from data.models import Posto,SerieOriginal,Variavel,Reducao,SerieTemporal,Discretizacao#,NivelConsistencia,Unidade,SerieReduzida
from .forms import FormSelecionaPosto,FormDadosPosto
from numpy import nan,mean
from django.db.models import Q
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



def filtra_temporais_por_originais(originais):
    queries = [Q(Id=o.serie_temporal_id) for o in originais]
    query = queries.pop()
    for item in queries:
        query |= item
    return query
    
dic = {"jan":"1","fev":"2"}


def dados_diarios_pandas(dados_temporais,obs):
    #dados_temporais = [d for d in dados_temporais if d.data_e_hora.year ==1982]
    dados = [o.dado if not o is None else nan for o in dados_temporais]
    datas = [o.data_e_hora for o in dados_temporais]
    niveis = [obs[o.Id] for o in dados_temporais]
    #d=pd.date_range(start=min(datas),end=max(datas))
    #print(d)
    pf = pd.DataFrame({"dado" : dados,"nivel":niveis}, index=pd.DatetimeIndex(datas))
    gp = pd.Grouper(freq='D')
    pfgp = pf.groupby(gp).mean()
    return pfgp

def sugere_mes_inicio_ano_hidrologico(df):
    medias_por_mes={i:df[df.index.month==i].mean().item() for i in range(1,13)}
    return min(medias_por_mes.items(),key=lambda x:x[1])[0]
    
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
    posto = Posto.objects.get(id=int(posto_id))
    if request.method == 'GET':
        originais = SerieOriginal.objects.filter(posto=posto)
        variaveis_disponiveis = [o.variavel for o in originais]
        variaveis =((variavel.id,variavel.variavel) for variavel in [v for v in Variavel.objects.all() if v in variaveis_disponiveis])
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
            print(list(set([i.Id for i in temporais])))
            pf = dados_diarios_pandas(temporais,obs)
            print(pf)
            nmes = sugere_mes_inicio_ano_hidrologico(pf)
            print("Mês:",nmes)
            gp = pd.Grouper(freq="AS-JUL")
            #discretizacao = Discretizacao.objects.get(codigo_pandas=dados['discretizacao'])
            #reducao = Reducao.objects.get(id=int(dados['reducao']))
            
            
            
            
            #print(pd.rolling_mean(pf, window=30, center=False))
            #print(pd.rolling_mean(pf, window=30, center=False))
            #gp = pd.Grouper(freq=discretizacao.codigo_pandas)
            
            
            pfgp = pf.groupby(gp)
            dic = dict(list(pfgp))
            anos_hidrologicos = {key.year:dic[key] for key in dic.keys()}
            #.agg(funcoes_reducao[reducao.tipo])
            
            #print(pd.DataFrame({'dados':list(anos_hidrologicos.values())},index=list(anos_hidrologicos.keys())))
            
            return render(request,'seleciona_dados_posto.html',{'aba':'postos','form':form})
    
    
    


    