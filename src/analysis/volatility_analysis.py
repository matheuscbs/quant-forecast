import logging

import numpy as np
from arch import arch_model
from arch.__future__ import reindexing
from src.analysis.i_analysis import IAnalysis


class VolatilityAnalysis(IAnalysis):
    def __init__(self, retornos):
        self.retornos = retornos
        self.logger = logging.getLogger(__name__)

    def analyze(self, models=['GARCH', 'EGARCH', 'TARCH'], p=1, q=1, horizon=30, simulations=1000):
        retornos = self.retornos.dropna() * 100
        best_model = None
        lowest_aic = np.inf
        all_forecasts = {}

        # Testando diferentes modelos e selecionando o melhor
        for model_name in models:
            try:
                model = arch_model(retornos, vol=model_name, p=p, q=q, dist='Normal')
                result = model.fit(disp='off')

                if result.aic < lowest_aic:
                    lowest_aic = result.aic
                    best_model = model_name

                # Simulações para cada modelo
                sim_forecast = result.forecast(horizon=horizon, method='simulation', simulations=simulations)
                all_forecasts[model_name] = sim_forecast.variance.iloc[-1]
            except Exception as e:
                self.logger.warning(f"Erro ao ajustar o modelo {model_name}: {e}")

        if best_model:
            self.logger.info(f"Melhor modelo selecionado: {best_model} (AIC: {lowest_aic:.2f})")
            return all_forecasts  # Retorna previsões de todos os modelos para análise comparativa
        else:
            self.logger.error("Nenhum modelo convergiu com sucesso.")
            return None
