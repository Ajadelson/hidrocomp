import pandas as pd
from numpy import nan,mean,argmax,argmin
from datetime import datetime
from abc import ABCMeta, abstractmethod
from data.models import Posto,SerieOriginal,Variavel,Reducao,SerieTemporal,Discretizacao,SerieReduzida#,NivelConsistencia,Unidade


funcoes_reducao = {'máxima':max,'mínima':min,'soma':sum, 'média':mean,'máxima média móvel':argmax,'mínima média móvel':argmin,
                  'ascencao':'>','reducao':'<','reversao':'change'}
meses = {1:"JAN",2:"FEB",3:"MAR",4:"APR",5:"MAY",6:"JUN",7:"JUL",8:"AUG",9:"SEP",10:"OCT",11:"NOV",12:"DEC"}


class BaseEcoHidro(metaclass=ABCMeta):
    def __init__(self,posto):
        self.posto = posto
        variaveis_disponiveis = [o.variavel for o in SerieOriginal.objects.filter(posto=posto)]
        self.variaveis =((variavel.id,variavel.variavel) for variavel in [v for v in Variavel.objects.all() if v in variaveis_disponiveis])
    
    @abstractmethod
    def atualiza_informacoes(self):
        pass
    
    def pegar_serie_original(self,variavel_id):
        self.variavel=Variavel.objects.get(id=variavel_id)
        originais = SerieOriginal.objects.filter(posto=self.posto,variavel=self.variavel)
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
            maior_id_original = SerieOriginal.objects.latest('serie_temporal_id').serie_temporal_id
            maior_id_reduzida = SerieReduzida.objects.latest('serie_temporal_id').serie_temporal_id
            maior_id_temporal = SerieTemporal.objects.latest('Id').Id
            return max([maior_id_original,maior_id_reduzida,maior_id_temporal])+1
        else:
            return 1

    def sugere_mes_inicio_ano_hidrologico(self,df):
        medias_por_mes = df["dado"].groupby(pd.Grouper(freq='M')).mean()
        minimas_dos_anos = df.groupby(pd.Grouper(freq='AS')).idxmin()
        return pd.value_counts([d.month for d in minimas_dos_anos["dado"]]).idxmax()
    
    def criar_temporal(self,dados,datas):
        Id = self.get_id_temporal()
        dados_temporais = list(zip(datas,dados))
        print("Criando série temporal id = %i"%Id)
        for e in dados_temporais:
            print(e[0],e[1])
        SerieTemporal.objects.bulk_create([
                            SerieTemporal(Id = Id,data_e_hora = e[0],dado = e[1]) for e in dados_temporais if not e[0] is nan 
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
    
    @abstractmethod
    def prepara_serie_reduzida(self):
        pass
    
    def obtem_dados_temporais(self,dados,datas):
        Id = self.criar_temporal(dados,datas)
        self.serie_reduzida = SerieReduzida.objects.create(
                serie_original = self.original,
                discretizacao = self.discretizacao,
                reducao = self.reducao,
                serie_temporal_id = Id
        )
        self.serie_reduzida.save()
        return SerieTemporal.objects.filter(Id=Id)
        
        
        
class EstatisticaBasica(BaseEcoHidro):
    def atualiza_informacoes(self,codigo_discretizacao,reducao_id):
        self.discretizacao = Discretizacao.objects.get(codigo_pandas=codigo_discretizacao)
        self.reducao = Reducao.objects.get(id=reducao_id)
    
    def prepara_serie_reduzida(self):
        temporais = SerieTemporal.objects.filter(Id=self.original.serie_temporal_id)
        diarios = self.cria_dados_diarios_pandas(temporais) 
        gp = pd.Grouper(freq=self.discretizacao.codigo_pandas)
        mensais = diarios.groupby(gp).agg(funcoes_reducao[self.reducao.tipo])
        datas = list(mensais.index)
        dados = list(mensais["dado"])
        return self.obtem_dados_temporais(dados,datas)
    

class MediaMovel(BaseEcoHidro):
    def atualiza_informacoes(self,variavel_id,tipo_media_movel,codigo_discretizacao_media_movel):
        self.discretizacao = Discretizacao.objects.get(codigo_pandas="AS")
        self.reducao = Reducao.objects.get(tipo=tipo_media_movel+" média móvel")
        self.discretizacao_media_movel=codigo_discretizacao_media_movel
    
    def prepara_serie_reduzida(self):
        temporais = SerieTemporal.objects.filter(Id=self.original.serie_temporal_id)
        diarios = self.cria_dados_diarios_pandas(temporais)
        médias_móveis_por_dia = diarios.rolling(window=int(self.discretizacao_media_movel),center=False).mean()
        anos_hidrologicos = self.dicionario_de_anos_hidrologicos(médias_móveis_por_dia)
        gp = pd.Grouper(freq="10AS")
        anos = sorted(list(anos_hidrologicos.keys()))
        dados = [anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo.split()[0]]).max()
                 for ano in anos if not anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo.split()[0]]) is (nan)]
        datas = [anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo]).max()
                 for ano in anos  if not anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo.split()[0]]) is (nan)]
        return self.obtem_dados_temporais(dados,datas)
    
class RazaoMudanca(BaseEcoHidro):
    def atualiza_informacoes(self,variavel_id,reducao_id):
        self.discretizacao = Discretizacao.objects.get(codigo_pandas="AS")
        self.reducao = Reducao.objects.get(id=reducao_id)
        
    def prepara_serie_reduzida(self):
        temporais = SerieTemporal.objects.filter(Id=self.original.serie_temporal_id)
        diarios = self.cria_dados_diarios_pandas(temporais)
        anos_hidrologicos = self.dicionario_de_anos_hidrologicos(diarios)
        anos = sorted(list(anos_hidrologicos.keys()))
        dados = []
        for ano in anos:
            df = anos_hidrologicos[ano]
            df=pd.DataFrame({'dado':df.values},index=df.index)
            df['dif'] = df['dado'] - df['dado'].shift(1)
            r = df[df['dif']>0]['dado'].mean()
            print(r)
            dados.append(float(r))
        datas = [datetime(ano,1,1) for ano in anos]
        return self.obtem_dados_temporais(dados,datas)
    
#events = np.split(a['dif'], np.where(a['dif']>a['dif'].shift(1))[0])
    
    
    
    
    
    
    
'''
class EcoHidro(object):
    def __init__(self,posto):
        self.posto = posto
        variaveis_disponiveis = [o.variavel for o in SerieOriginal.objects.filter(posto=posto)]
        self.variaveis =((variavel.id,variavel.variavel) for variavel in [v for v in Variavel.objects.all() if v in variaveis_disponiveis])
    
    def pegar_serie_original(self,variavel_id,codigo_discretizacao,reducao_id,tipo_media_movel,codigo_discretizacao_media_movel):
        self.variavel=Variavel.objects.get(id=variavel_id)
        originais = SerieOriginal.objects.filter(posto=self.posto,variavel=self.variavel)
        self.discretizacao = Discretizacao.objects.get(codigo_pandas=codigo_discretizacao)
        print(tipo_media_movel)
        if tipo_media_movel:
            self.reducao = Reducao.objects.get(tipo=tipo_media_movel+" média móvel")
            self.discretizacao_media_movel=codigo_discretizacao_media_movel
            
        else:
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
            maior_id_original = SerieOriginal.objects.latest('serie_temporal_id').serie_temporal_id
            maior_id_reduzida = SerieReduzida.objects.latest('serie_temporal_id').serie_temporal_id
            maior_id_temporal = SerieTemporal.objects.latest('Id').Id
            return max([maior_id_original,maior_id_reduzida,maior_id_temporal])+1
        else:
            return 1

    def sugere_mes_inicio_ano_hidrologico(self,df):
        medias_por_mes = df["dado"].groupby(pd.Grouper(freq='M')).mean()
        minimas_dos_anos = df.groupby(pd.Grouper(freq='AS')).idxmin()
        return pd.value_counts([d.month for d in minimas_dos_anos["dado"]]).idxmax()
    
    def criar_temporal(self,dados,datas):
        Id = self.get_id_temporal()
        dados_temporais = list(zip(datas,dados))
        print("Criando série temporal id = %i"%Id)
        for e in dados_temporais:
            print(e[0],e[1])
        SerieTemporal.objects.bulk_create([
                            SerieTemporal(Id = Id,data_e_hora = e[0],dado = e[1]) for e in dados_temporais if not e[0] is nan 
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
        if "média móvel" in self.reducao.tipo:
            print(self.discretizacao)
            médias_móveis_por_dia = diarios.rolling(window=int(self.discretizacao_media_movel),center=False).mean()
            anos_hidrologicos = self.dicionario_de_anos_hidrologicos(médias_móveis_por_dia)
            gp = pd.Grouper(freq="10AS")
            anos = sorted(list(anos_hidrologicos.keys()))
            dados = [anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo.split()[0]]).max()
                     for ano in anos if not anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo.split()[0]]) is (nan)]
            datas = [anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo]).max()
                     for ano in anos  if not anos_hidrologicos[ano].groupby(gp).agg(funcoes_reducao[self.reducao.tipo.split()[0]]) is (nan)]
            print(dados)
            print(datas)
            #datas = list(anos_hidrologicos.idxmax())
            #dados = anos_hidrologicos.max()
        else: 
            gp = pd.Grouper(freq=self.discretizacao.codigo_pandas)
            mensais = diarios.groupby(gp).agg(funcoes_reducao[self.reducao.tipo])
            datas = list(mensais.index)
            dados = list(mensais["dado"])

        Id = self.criar_temporal(dados,datas)
        r = SerieReduzida.objects.create(
                serie_original = self.original,
                discretizacao = self.discretizacao,
                reducao = self.reducao,
                serie_temporal_id = Id
        )
        r.save()
        return SerieTemporal.objects.filter(Id=Id)
    '''