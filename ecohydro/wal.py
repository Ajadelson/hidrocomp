def prepara_serie_reduzida(self):
    médias_móveis_por_dia = "ISSO É A VARIÁVEL COM AS MÁXIMAS MÉDIA MÓVEIS QUE VOCê JÁ TEM"
    #tranforma em dicionáriod e anos hidrológicos
    anos_hidrologicos = self.dicionario_de_anos_hidrologicos(médias_móveis_por_dia)
    anos = sorted(list(anos_hidrologicos.keys()))
    dados = [anos_hidrologicos[ano].max() for ano in anos if anos_hidrologicos[ano].max() is not(nan)]
    datas = [anos_hidrologicos[ano].idxmax() for ano in anos  if anos_hidrologicos[ano].max() is not(nan)]
    Id = self.criar_temporal(dados,datas)
    r = SerieReduzida.objects.create(
            serie_original = self.original,
            discretizacao = self.discretizacao,
            reducao = self.reducao,
            serie_temporal_id = Id
    )
    r.save()