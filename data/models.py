from django.db import models


class Coordenada(models.Model):
    x = models.FloatField()
    y = models.FloatField()


class Localizacao(models.Model):
    coordenadas = models.ForeignKey(Coordenada)
    """
    coordenadas = models.PointField(srid=4326)
    objects = models.GeoManager()
    """

    def __unicode__(self):
        return '%s %s' % (self.coordenadas.x, self.coordenadas.y)

    
from django.utils.translation import ugettext_lazy as _

'''#################### **************** SÉRIE TEMPORAL *************** #####################'''

class SerieTemporal(models.Model):
    Id = models.IntegerField(unique=False)
    dado = models.FloatField(null=True)
    data_e_hora = models.DateTimeField(verbose_name = 'Data e Hora',unique=False)
    class Meta:
        unique_together = (("Id","data_e_hora"),)
        verbose_name_plural = "Séries Temporais"
        verbose_name = "Série Temporal"
        
#ids = [n.Id for n in SerieTemporal.objects.all()]
#choices = ((str(n),str(n)) for n in set(ids))

'''#################### **************** POSTO *************** #####################'''
class TipoPosto(models.Model):
    tipo = models.CharField(max_length=20)
    class Meta:
        verbose_name_plural = "Tipos de Posto"
        verbose_name = "Tipo de Posto"
    def __str__(self):
        return '%s'%self.tipo
class Fonte(models.Model):
    tipo = models.CharField(max_length=15)
    def __str__(self):
        return '%s'%self.tipo

class Posto(models.Model):
    tipo_posto = models.ForeignKey(TipoPosto)
    fonte = models.ForeignKey(Fonte)
    codigo_ana = models.CharField(max_length=15,null=True)
    nome = models.CharField(max_length=100)
    localizacao = models.ForeignKey(Localizacao)
    def __str__(self):
        return '%s %s (%s)'%(self.nome,self.fonte.tipo,self.codigo_ana)

'''#################### **************** PRÉ-REQUISITOS PARA SÉRIE ORIGINAL E REDUZIDA *************** #####################'''
class Discretizacao(models.Model):
    tipo = models.CharField(max_length=20)
    codigo_pandas = models.CharField(max_length=20)
    class Meta:
        verbose_name_plural = "Discretizações"
        verbose_name = "Discretização"
    def __str__(self):
        return '%s'%self.tipo
    
    
class Unidade(models.Model):
    tipo = models.CharField(max_length=20)
    class Meta:
        verbose_name_plural = "Unidades de Medida"
        verbose_name = "Unidade de Medida"
    def __str__(self):
        return '%s'%self.tipo
    
    
class Variavel(models.Model):
    variavel = models.CharField(max_length=20)
    codigo_ana = models.CharField(max_length=2)
    class Meta:
        verbose_name_plural = "Variáveis"
        verbose_name = "Variável"
    def __str__(self):
        return '%s'%self.variavel
class NivelConsistencia(models.Model):
    tipo = models.CharField(max_length=20)
    class Meta:
        verbose_name_plural = "Níveis de Consistência"
        verbose_name = "Nível de Consistência"
    def __str__(self):
        return '%s'%self.tipo
class Reducao(models.Model):
    tipo = models.CharField(max_length=20)
    class Meta:
        verbose_name_plural = "Reduções"
        verbose_name = "Redução"
    def __str__(self):
        return '%s'%self.tipo
'''#################### **************** SÉRIE ORIGINAL *************** #####################'''

class SerieOriginal(models.Model):
    posto = models.ForeignKey(Posto)
    arquivo_Fonte_data = models.DateTimeField(auto_now_add=True,verbose_name = 'Data e Hora',unique=False)
    variavel = models.ForeignKey(Variavel)
    tipo_dado = models.ForeignKey(NivelConsistencia)
    discretizacao = models.ForeignKey(Discretizacao)
    unidade = models.ForeignKey(Unidade)
    serie_temporal_id = models.IntegerField()
    def __str__(self):
        return 'Série Original %s do posto de %s, com dados de %s (%s)'%(self.discretizacao.tipo,self.posto,self.variavel,self.unidade)
    
    class Meta:
        verbose_name_plural = "Séries Originais"
        verbose_name = "Série Original"

'''#################### **************** SÉRIE REDUZIDA *************** #####################'''


class SerieReduzida(models.Model):
    serie_original = models.ForeignKey(SerieOriginal)
    discretizacao = models.ForeignKey(Discretizacao)
    reducao = models.ForeignKey(Reducao)
    serie_temporal_id = models.IntegerField()
    class Meta:
        verbose_name_plural = "Séries Reduzidas"
        verbose_name = "Série Reduzida"
    def __str__(self):
        return 'Série de %s %s do posto de %s'%(self.reducao.tipo,self.discretizacao.tipo,
                                                                      self.serie_original.posto)


