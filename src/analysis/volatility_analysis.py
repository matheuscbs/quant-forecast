from arch import arch_model
from arch.__future__ import reindexing
from src.analysis.i_analysis import IAnalysis


class VolatilityAnalysis(IAnalysis):
    def __init__(self, retornos):
        self.retornos = retornos

    def analyze(self):
        retornos = self.retornos.dropna() * 100
        modelo_garch = arch_model(retornos, vol='Garch', p=1, q=1, dist='Normal')
        resultado_garch = modelo_garch.fit(disp='off')
        previsao_volatilidade = resultado_garch.forecast(horizon=30, method='simulation')
        futura_volatilidade = previsao_volatilidade.variance.iloc[-1]
        return futura_volatilidade
