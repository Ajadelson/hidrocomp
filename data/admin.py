from django.contrib import admin
from .models import Discretizacao,Reducao,Posto,Fonte,TipoPosto,Localizacao,Unidade,Variavel,NivelConsistencia,SerieReduzida,SerieOriginal,Coordenada

class TipoPostoAdmin(admin.ModelAdmin):
    model = TipoPosto
    list_display = ['tipo']
    search_fields = ['tipo']
    save_on_top = True
class FonteAdmin(admin.ModelAdmin):
    model = Fonte
    list_display = ['tipo']
    search_fields = ['tipo']
    save_on_top = True
class LocalizacaoAdmin(admin.ModelAdmin):
    model = Localizacao
    list_display = ['coordenadas']
    #search_fields = ['tipo']
    save_on_top = True
class PostoAdmin(admin.ModelAdmin):
    model = Posto
    list_display = ['nome','tipo_posto','fonte','codigo_ana','localizacao']
    search_fields = ['nome']
    save_on_top = True

class UnidadeAdmin(admin.ModelAdmin):
    model = Unidade
    list_display = ['tipo']
    search_fields = ['tipo']
    save_on_top = True
class VariavelAdmin(admin.ModelAdmin):
    model = Variavel
    list_display = ['variavel']
    search_fields = ['variavel']
    save_on_top = True
class NivelConsistenciaAdmin(admin.ModelAdmin):
    model = NivelConsistencia
    list_display = ['tipo']
    search_fields = ['tipo']
    save_on_top = True
class DiscretizacaoAdmin(admin.ModelAdmin):
    model = Discretizacao
    list_display = ['tipo']
    search_fields = ['tipo']
    save_on_top = True
class ReducaoAdmin(admin.ModelAdmin):
    model = Reducao
    list_display = ['tipo']
    search_fields = ['tipo']
    save_on_top = True

class SerieReduzidaAdmin(admin.ModelAdmin):
    model = SerieReduzida
    list_display = ['serie_original','discretizacao','reducao','serie_temporal_id']
    search_fields = ['serie_original__id']
    save_on_top = True

class SerieOriginalAdmin(admin.ModelAdmin):
    model = SerieOriginal
    #list_display = ['Discretizacao_','Unidade_','Variavel_','Tipo_Dado_','serie_Temporal_id']
    list_display = ['serie_temporal_id','posto','discretizacao','variavel','unidade','tipo_dado']
    search_fields = ['serie_Temporal_id']
    save_on_top = True



admin.site.register(TipoPosto,TipoPostoAdmin)
admin.site.register(Coordenada)
admin.site.register(Fonte,FonteAdmin)
admin.site.register(Localizacao)
admin.site.register(Posto,PostoAdmin)
admin.site.register(Unidade,UnidadeAdmin)
admin.site.register(Variavel,VariavelAdmin)
admin.site.register(NivelConsistencia,NivelConsistenciaAdmin)
admin.site.register(Discretizacao,DiscretizacaoAdmin)
admin.site.register(Reducao,ReducaoAdmin)
admin.site.register(SerieOriginal,SerieOriginalAdmin)
admin.site.register(SerieReduzida,SerieReduzidaAdmin)
