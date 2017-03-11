import pandas as pd
from data.models import Posto,SerieOriginal,Variavel,Reducao,SerieTemporal,Discretizacao,SerieReduzida#,NivelConsistencia,Unidade
from numpy import nan,mean

funcoes_reducao = {'máxima':max,'mínima':min,'soma':sum, 'média':mean}
meses = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}

class EcoHidro(object):
    def __init__(self,posto):
        self.posto = posto
        variaveis_disponiveis = [o.variavel for o in SerieOriginal.objects.filter(posto=posto)]
        self.variaveis =((variavel.id,variavel.variavel) for variavel in [v for v in Variavel.objects.all() if v in variaveis_disponiveis])
    
    def pegar_serie_original(self,variavel_id,codigo_discretizacao,reducao_id):
        self.variavel=Variavel.objects.get(id=variavel_id)
        originais = SerieOriginal.objects.filter(posto=self.posto,variavel=self.variavel)
        self.discretizacao = Discretizacao.objects.get(codigo_pandas=codigo_discretizacao)
        self.reducao = Reducao.objects.get(id=reducao_id)
        id_tipo_dado = 2 if 2 in [o.tipo_dado.id for o in originais] else 1
        self.original = [o for o in originais if o.tipo_dado.id == id_tipo_dado][0]
        return self.original
    def cria_dados_diarios_pandas(self,dados_temporais):
        self.dados_temporais = dados_temporais
        dados = [o.dado if not o is None else nan for o in dados_temporais]
        datas = [o.data_e_hora for o in dados_temporais]
        pf = pd.DataFrame({"dado" : dados}, index=pd.DatetimeIndex(datas))
        gp = pd.Grouper(freq='D',sort=True)
        self.dados_diarios = pf.groupby(gp).mean()
        return self.dados_diarios
    def get_id_temporal(self):
        if SerieOriginal.objects.count()>0:
            o = [o.serie_temporal_id for o in SerieOriginal.objects.all()]
            r = [o.serie_temporal_id for o in SerieReduzida.objects.all()]
            if r:
                o.extend(r)
            return max(o)+1
        else:
            return 1



    def sugere_mes_inicio_ano_hidrologico(self,df):
        medias_por_mes = df["dado"].groupby(pd.Grouper(freq='M')).mean()
        minimas_dos_anos = df.groupby(pd.Grouper(freq='AS')).idxmin()
        return pd.value_counts([d.month for d in minimas_dos_anos["dado"]]).idxmax()
    def criar_temporal(self,dados,datas):
        Id = get_id_temporal()
        dados_temporais = list(zip(datas,dados))
        print("Criando série temporal id = %i"%Id)
        for e in dados_temporais:
            print(e[0],e[1])
        SerieTemporal.objects.bulk_create([
                            SerieTemporal(Id = Id,data_e_hora = e[0],dado = e[1]) for e in dados_temporais
                    ])
        print("criado")
        return Id
    def dicionario_de_anos_hidrologicos(self,df):
        nmes = self.sugere_mes_inicio_ano_hidrologico(df)
        gp = df["dado"].groupby(pd.Grouper(freq="AS-%s"%meses[nmes]))
        dic = dict(list(gp))
        anos_hidrologicos = {key.year:dic[key] for key in dic.keys()}
        return anos_hidrologicos
    def obter_series_reduzidas(self):
        return SerieReduzida.objects.filter(
                serie_original = self.original,discretizacao=self.discretizacao,reducao=self.reducao)
        
    
    
    def prepara_serie_reduzida(self):
        temporais = SerieTemporal.objects.filter(Id=self.original.serie_temporal_id)
        diarios = self.cria_dados_diarios_pandas(temporais)
        if self.reducao.tipo=="média móvel":
            médias_móveis_por_dia = diarios.rolling(window=int(self.discretizacao.codigo_pandas),center=False).mean()
            anos_hidrologicos = self.dicionario_de_anos_hidrologicos(médias_móveis_por_dia)
            anos = sorted(list(anos_hidrologicos.keys()))
            dados = [anos_hidrologicos[ano].max() for ano in anos if anos_hidrologicos[ano].max() is not(nan)]
            datas = [anos_hidrologicos[ano].idxmax() for ano in anos  if anos_hidrologicos[ano].max() is not(nan)]
            #datas = list(anos_hidrologicos.idxmax())
            #dados = anos_hidrologicos.max()
        else: 
            gp = pd.Grouper(freq=self.discretizacao.codigo_pandas+"S")
            mensais = diarios.groupby(gp).agg(funcoes_reducao[reducao.tipo])
            datas = list(mensais.index)
            dados = list(mensais["dado"])

        Id = self.criar_temporal(dados,datas)
        r = SerieReduzida.objects.create(
                serie_original = self.original,
                discretizacao = discretizacao,
                reducao = reducao,
                serie_temporal_id = Id
        )
        r.save()