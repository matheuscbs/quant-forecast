import logging

import pandas as pd
from prophet.diagnostics import cross_validation
from src.analysis.i_analysis import IAnalysis
from src.optimization.data_granularity_checker import DataGranularityChecker
from src.optimization.data_preparation import DataPreparation
from src.optimization.hyperparameter_optimization import OptunaOptimization

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProphetAnalysis(IAnalysis):
    def __init__(self, ticker, data, future_periods, country_name='BR'):
        self.ticker = ticker
        self.data = data
        self.future_periods = future_periods
        self.country_name = country_name
        self.optuna_optimization = OptunaOptimization(country_name=country_name)
        self.model = None
        self.forecast = None

    def optimize_and_fit(self):
        """Otimiza os hiperparâmetros e ajusta o modelo aos dados."""
        try:
            logging.info("Starting hyperparameter optimization and model fitting")
            best_params = self.optuna_optimization.optimize(self.data, self.future_periods)
            is_intraday = DataGranularityChecker.is_intraday(self.data)
            self.model = self.optuna_optimization._create_model(best_params, is_intraday)
            self.model.fit(self.data)
            logging.info("Model fitted successfully with best parameters.")
        except Exception as e:
            logging.error(f"Error during optimization and fitting: {e}")
            raise  # Re-raise the exception for better debugging

    def cross_validate_model(self):
        """Realiza a validação cruzada do modelo."""
        logging.info("Starting cross-validation")
        is_intraday = DataGranularityChecker.is_intraday(self.data)
        initial, period, horizon = DataPreparation.calculate_adaptive_parameters(self.data, self.future_periods, is_intraday)
        df_cv = cross_validation(self.model, initial=initial, period=period, horizon=horizon)
        logging.info("Cross-validation completed.")
        return df_cv

    def make_forecast(self):
        """Gera as previsões futuras."""
        logging.info("Generating forecasts")
        future = self.model.make_future_dataframe(periods=self.future_periods)
        self.forecast = self.model.predict(future)
        return self.forecast

    def run_analysis(self):
        """Executa a análise completa: otimização, ajuste, validação cruzada e previsão."""
        if isinstance(self.data, pd.DataFrame) and not self.data.empty:
            self.optimize_and_fit()
            df_cv = self.cross_validate_model()
            forecast = self.make_forecast()
            return self.model, forecast, df_cv
        else:
            logging.error("Analysis cannot be completed due to data preparation issues.")
            return None, None, None

    def analyze(self):
        """Ponto de entrada para a análise."""
        return self.run_analysis()
