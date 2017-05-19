import os
from abc import ABCMeta, abstractmethod
import requests
import re
import shutil
import pandas as pd
import calendar
import numpy as np
from bs4 import BeautifulSoup
import os
from datetime import datetime
from zipfile import ZipFile
from shutil import move
import sys
from tempfile import mkdtemp
from .models import Variavel,SerieTemporal,SerieOriginal,SerieReduzida,Posto,Discretizacao,Unidade,NivelConsistencia

def mes_em_numero(string):
    """CRIA O DATAFRAME DATAS - VAZÕES"""
    mes_num = {"jan":"1","fev":"2","mar":"3","abr":"4","mai":"5","jun":"6","jul":"7","ago":"8","set":"9","out":"10","nov":"11","dez":"12"}
    for mes,num in mes_num.items():
        string=string.replace(mes,num)
    return string

def get_id_temporal():
    """Função que retorna ID para ser usado na série Temporal"""
    if SerieOriginal.objects.count()>0:
        maior_id_original = SerieOriginal.objects.latest('serie_temporal_id').serie_temporal_id
        maior_id_reduzida = SerieReduzida.objects.latest('serie_temporal_id').serie_temporal_id
        maior_id_temporal = SerieTemporal.objects.latest('Id').Id
        return max([maior_id_original,maior_id_reduzida,maior_id_temporal])+1
    else:
        return 1
    
def criar_temporal(dados,datas):
    """Cria a série Temporal série Temporal"""
    Id = get_id_temporal()
    dados_temporais = list(zip(datas,dados))
    print("Criando série temporal id = %i"%Id)
    SerieTemporal.objects.bulk_create([
                        SerieTemporal(Id = Id,data_e_hora = e[0],dado = e[1]) for e in dados_temporais
                ])
    print("criado")
    return Id

def cria_serie_original(dados,datas,posto,variavel,nivel_consistencia):
    """Cria a série Original a partir de um DataFrame"""
    Id = criar_temporal(dados,datas)
    print("Criando Série Original para a temporal de ID: "+str(Id))
    o = SerieOriginal.objects.create(
            posto = posto,
            discretizacao = Discretizacao.objects.get(tipo="diário"),
            variavel = variavel,
            serie_temporal_id = Id,
            unidade=Unidade.objects.get(tipo="m³/s"),
            tipo_dado = NivelConsistencia.objects.get(id=nivel_consistencia)
    )
    o.save()
    return o


class Base(metaclass=ABCMeta):
    @abstractmethod
    def le_dados(self,temp_dir):
        pass
    
    @abstractmethod
    def obtem_nome_posto(self,estacao):
        pass
    
    @abstractmethod
    def executar(self,posto,variavel):
        pass
    
    

class ONS(Base):
    def le_dados(self,temp_dir):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        planilha=pd.read_excel(os.path.join(dir_path,"Vazões_Diárias_1931_2015.xls"),skiprows=7,header=None)
        #CRIANDO A COLUNA DE DATAS
        data=list(map(mes_em_numero,list(planilha[0])))
        #setlocale(LC_TIME,'portuguese_brazil')
        #TRANSFORMANDO EM UM INDEX DE DATAS
        data=pd.DatetimeIndex(pd.to_datetime(pd.Series(data), format="%d/%m/%Y"))
        #CRIA A COLUNA DE VAZÃO
        vazao=planilha[150]
        #CRIANDO DATAFRAME - DATAS COMO INDICE DAS VAZÕES
        df = pd.DataFrame({"Vazão":list(vazao)},index = data)
        return df
    def obtem_nome_posto(self,estacao):
        return "Xingó",False
    def executar(self,posto,variavel):
        if variavel.variavel != "Vazão":
            return "Não existe a variável do tipo '%s' neste posto"%str(variavel)
        print ('** %s **' % (posto.codigo_ana, )) 
        df = self.le_dados('Temp_dir')
        cria_serie_original(df.values,df.index,posto,variavel,1)
        print ('** %s ** (concluído)' % (posto.codigo_ana,))

class ANA(Base):

    url_estacao = 'http://hidroweb.ana.gov.br/Estacao.asp?Codigo={0}&CriaArq=true&TipoArq={1}'
    url_arquivo = 'http://hidroweb.ana.gov.br/{0}'
        

    def montar_url_estacao(self, estacao, tipo=1):
        return self.url_estacao.format(estacao, tipo)

    def montar_url_arquivo(self, caminho):
        return self.url_arquivo.format(caminho)

    def montar_nome_arquivo(self, estacao):
        return u'{0}.zip'.format(estacao)
        
    
    def  extrai_e_renomeia(self,filename,temp_dir):
        '''Esta função recebe como argumento um arquivo ".zip" para extrair e renomear'''
        zip_path = os.path.join(temp_dir,filename)
        extraction_dir = os.path.join(os.getcwd(), os.path.splitext(filename)[0])
        with ZipFile(zip_path, 'r') as zip_file:
            # Build a list of only the members below ROOT_PATH
            members = zip_file.namelist()
            members_to_extract = [m for m in members]
            # Extract only those members to the temp directory
            zip_file.extractall(temp_dir, members_to_extract)
            # Move the extracted ROOT_PATH directory to its final location
            
            os.rename(os.path.join(temp_dir,members_to_extract[0]),os.path.join(temp_dir,self.estacao))

    def salvar_arquivo_texto(self, estacao, link):
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
            filename=self.montar_nome_arquivo(estacao)
            temp_dir = mkdtemp()
            with open(os.path.join(temp_dir,filename), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            print ('** %s ** (baixado)' % (estacao, ))
            self.extrai_e_renomeia(filename,temp_dir)               
            print ('** %s ** (decompactado)' % (estacao, ))
        else:
            print ('** %s ** (problema)' % (estacao, ))
        return temp_dir
    
    def le_dados(self,temp_dir):
        lista_series_mensais_por_cons={1:[],2:[]}
        with open(os.path.join(temp_dir,self.estacao),'rt') as file:
            for linha in file.readlines():
                if(linha.startswith("\n") or linha.startswith("/")):
                    continue
                s=linha.replace(',','.').split(";")
                if s[3]:
                    data_linha=datetime.strptime(s[2]+" "+s[3].split()[-1], '%d/%m/%Y %H:%M:%S')
                else:
                    data_linha=datetime.strptime(s[2],'%d/%m/%Y')
                dias_no_mes=calendar.monthrange(data_linha.year,data_linha.month)
                rng=pd.DatetimeIndex(pd.date_range(data_linha,periods=dias_no_mes[1], freq='D'))
                cons=[int(s[1]) for i in range (dias_no_mes[1])]
                serie_linha=pd.Series(s[16:16+dias_no_mes[1]],index=rng)
                lista_series_mensais_por_cons[int(s[1])].append(serie_linha)
        serie_completa_por_niv = {}
        for i in lista_series_mensais_por_cons:
            if lista_series_mensais_por_cons[i]:
                serie_completa=pd.concat(lista_series_mensais_por_cons[i])
                serie_completa=pd.to_numeric(serie_completa, errors='coerce', downcast='float')
                serie_completa.sort_index(inplace=True)     
                definicao_de_duplicatas=serie_completa.reset_index(level=1, drop=True).index.duplicated(keep='last')
                serie_completa_por_niv[i]=serie_completa[~definicao_de_duplicatas]
        return serie_completa_por_niv
    def obter_link_arquivo(self, response):
        soup = BeautifulSoup(response.content, "lxml")
        try:
            return soup.find('a', href=re.compile('^ARQ/'))['href'],False
        except:
            return 1,True
            
    def obtem_nome_posto(self,estacao):
        response = requests.get(self.montar_url_estacao(estacao))
        soup = BeautifulSoup(response.content, "lxml")
        try:
            menu = {t.text:t.find_next_sibling("td").text for t in soup.findAll("td",{'class':'gridCampo'})}
            return menu['Nome'],False
        except:
            return soup.findAll("p",{'class':'aviso'}),True
        

    def executar(self,posto,variavel=None):
        #post_datas = [{'cboTipoReg': variavel.codigo_ana} for variavel in Variavel.objects.all()]
        #for post_data in post_datas:
        self.estacao = posto.codigo_ana
        post_data={'cboTipoReg': variavel.codigo_ana}
        print ('** %s **' % (posto.codigo_ana, ))
        r = requests.post(self.montar_url_estacao(posto.codigo_ana), data=post_data)
        link,erro = self.obter_link_arquivo(r)
        if erro:
            return "Não existe a variável do tipo '%s' neste posto"%str(variavel)
        temp_dir = self.salvar_arquivo_texto(posto.codigo_ana, link)
        series = self.le_dados(temp_dir)
        for i in series:
            cria_serie_original(series[i].values,series[i].index,posto,variavel,i)
        print ('** %s ** (concluído)' % (self.estacao,))
            
            