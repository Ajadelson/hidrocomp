# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from .models import Fonte,Variavel,Posto,Localizacao,TipoPosto
from django.utils.safestring import mark_safe


class FormCriaSerieDeDados(forms.Form):
    #arquivo = forms.FileField(label="Arquivo:", error_messages={'required':'Por favor, Insira o arquivo!'}, 
    #                       #widget=forms.TextInput(
    #        #attrs={'class':'inputFormulario','style':'font-family:futura;width:100%;','placeholder':'Nome Completo',})
    #                       )
    """Choices"""
    postos = ((posto.codigo_ana,posto.nome) for posto in Posto.objects.all())
    variaveis = ((variavel.codigo_ana,variavel.variavel) for variavel in Variavel.objects.all())
    fontes = ((fonte.id,fonte.tipo) for fonte in Fonte.objects.all())
    
    """Campos do Formulário"""
    posto = forms.ChoiceField(label=mark_safe('Posto: (<a href="/postos/novo/" target="_blank">Criar Novo</a>)'),choices=postos)
    tipo_de_dado = forms.ChoiceField(label="Tipo de dado:",choices=variaveis)
    fonte = forms.ChoiceField(label="Fonte:",choices=fontes)


class FormCriaPosto(forms.Form):
    #arquivo = forms.FileField(label="Arquivo:", error_messages={'required':'Por favor, Insira o arquivo!'}, 
    #                       #widget=forms.TextInput(
    #        #attrs={'class':'inputFormulario','style':'font-family:futura;width:100%;','placeholder':'Nome Completo',})
    #                       )
    """Choices"""
    tipos_postos = ((tipo.id,tipo.tipo) for tipo in TipoPosto.objects.all())
    #localizacoes = ((loc.id,"localização") for loc in Localizacao.objects.all())
    fontes = ((fonte.id,fonte.tipo) for fonte in Fonte.objects.all())
    
    """Campos do Formulário"""
    tipo_posto = forms.ChoiceField(label="Tipo de posto:",choices=tipos_postos)
    fonte = forms.ChoiceField(label="Fonte:",choices=fontes)
    codigo_ana = forms.CharField(label="Código ANA:",required=False)
    #nome = forms.CharField(label="Nomo do posto:")
    #localizacao = forms.ChoiceField(label="Localização:",choices=localizacoes)
    
    

