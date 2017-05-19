# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from data.models import Posto,Discretizacao,Reducao#,SerieOriginal,SerieTemporal,Variavel,NivelConsistencia,Unidade,SerieReduzida


class FormSelecionaPosto(forms.Form):
    def __init__(self, postos=[], *args, **kwargs):
        super(FormSelecionaPosto, self).__init__(*args, **kwargs)
        self.fields['posto'].choices = postos        
    posto = forms.ChoiceField(label=mark_safe('Posto: (<a href="/postos/novo/" target="_blank">Criar Novo</a>)'))    

class FormDadosPosto(forms.Form):
    def __init__(self, variaveis=[], *args, **kwargs):
        super(FormDadosPosto, self).__init__(*args, **kwargs)
        self.fields['variavel'].choices =list(variaveis)
        reducoes = [[reducao.id,reducao.tipo] for reducao in Reducao.objects.all() if not 'média móvel' in reducao.tipo]+[[9999,"média móvel"],]
        discretizacoes = ((discretizacao.codigo_pandas,discretizacao.tipo) 
                          for discretizacao in Discretizacao.objects.all() if not discretizacao.tipo.lower().startswith("média móvel"))
        discretizacoes_media_movel = ((discretizacao.codigo_pandas,discretizacao.tipo) 
                          for discretizacao in Discretizacao.objects.all() if discretizacao.tipo.lower().startswith("média móvel"))
        self.fields['discretizacao_media_movel'].choices =list(discretizacoes_media_movel)
        self.fields['discretizacao'].choices =list(discretizacoes)
        self.fields['reducao'].choices =list(reducoes)
        
    
    

    variavel = forms.ChoiceField(label="Tipo de dado:")
    reducao = forms.ChoiceField(label="Redução:")
    discretizacao_media_movel = forms.ChoiceField(label="Discretizacao:",required=False,
                                         widget=forms.Select(attrs={'class':'média móvel'}))
    discretizacao = forms.ChoiceField(label="Discretizacao:",required=False,
                                         widget=forms.Select(attrs={'class':'média móvel'}))
    tipo_media_movel = forms.ChoiceField(label="Tipo de média móvel:",choices=(('',''),('máxima','máxima'),('mínima','mínima')),required=False,
                                         widget=forms.Select(attrs={'class':'média móvel'}))   