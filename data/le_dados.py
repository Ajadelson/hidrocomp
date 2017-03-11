import requests
import re
import shutil
from bs4 import BeautifulSoup
import os
from zipfile import ZipFile
from shutil import move
import sys
from tempfile import mkdtemp


class Dado(object):
    def __init__(self,data,dado,niv_consistencia):
        self.data=data
        self.dado=dado
        self.niv_consistencia=niv_consistencia
    def __str__(self):
        return '%i/%i/%i - %.2f - %i'%(self.data.day,self.data.month,self.data.year,self.dado,self.niv_consistencia)

   
class ONS(object):
    pass

class Hidroweb(object):

    url_estacao = 'http://hidroweb.ana.gov.br/Estacao.asp?Codigo={0}&CriaArq=true&TipoArq={1}'
    url_arquivo = 'http://hidroweb.ana.gov.br/{0}'

    def __init__(self, estacao):
        self.estacao = estacao

    def montar_url_estacao(self, estacao, tipo=1):
        return self.url_estacao.format(estacao, tipo)

    def montar_url_arquivo(self, caminho):
        return self.url_arquivo.format(caminho)

    def montar_nome_arquivo(self, estacao):
        return u'{0}.zip'.format(estacao)
    def obtem_nome_posto(self):
        pass
    
    def  extrai_e_renomeia(self,filename,temp_dir,estacao):
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
            cod=estacao
            
            os.rename(os.path.join(temp_dir,members_to_extract[0]),os.path.join(temp_dir,cod))
            move(os.path.join(temp_dir,cod), os.path.join(os.getcwd(),"%s.%s"%(cod,members_to_extract[0][0:3])))

    def salvar_arquivo_texto(self, estacao, link):
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
            filename=self.montar_nome_arquivo(estacao)
            temp_dir = mkdtemp()
            with open(os.path.join(temp_dir,filename), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            print ('** %s ** (baixado)' % (estacao, ))
            self.extrai_e_renomeia(filename,temp_dir,estacao)               
            print ('** %s ** (decompactado)' % (estacao, ))
        else:
            print ('** %s ** (problema)' % (estacao, ))
    def obter_link_arquivo(self, response):
        soup = BeautifulSoup(response.content, "lxml")
        return soup.find('a', href=re.compile('^ARQ/'))['href']

    def executar(self):
        self.estacao=est
        post_data = {'cboTipoReg': '10'}
        print ('** %s **' % (est, ))
        r = requests.post(self.montar_url_estacao(est), data=post_data)
        link = self.obter_link_arquivo(r)
        self.salvar_arquivo_texto(est, link)
        print ('** %s ** (concluído)' % (est, ))