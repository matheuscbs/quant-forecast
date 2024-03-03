import logging
from abc import ABC, abstractmethod

from prophet.diagnostics import cross_validation
from src.analysis.i_analysis import IAnalysis
from src.data.data_preparation import DataPreparation
from src.optimization.hyperparameter_optimization import OptunaOptimization
from src.plotting.plotter import Plotter

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
        self.plotter = Plotter()

    def optimize_and_fit(self):
        logging.info("Starting hyperparameter optimization")
        self.optuna_optimization.optimize(self.data, self.future_periods)
        self.model = self.optuna_optimization.best_model
        logging.info("Model fitted successfully with best parameters.")

    def cross_validate_model(self):
        logging.info("Starting cross-validation")
        initial, period, horizon = DataPreparation.calculate_adaptive_parameters(self.data, self.future_periods)
        df_cv = cross_validation(self.model, initial=initial, period=period, horizon=horizon)
        self.plotter.plot_cross_validation_metric(df_cv, "mape", "MAPE Metric")
        logging.info("Cross-validation completed.")

    def make_forecast(self):
        logging.info("Generating forecasts")
        future = self.model.make_future_dataframe(periods=self.future_periods)
        self.forecast = self.model.predict(future)

    def run_analysis(self):
        if self.data is not None:
            self.optimize_and_fit()
            self.cross_validate_model()
            self.make_forecast()
            self.plotter.plot_prophet_forecast(self.ticker, self.model, self.forecast)
        else:
            logging.error("Analysis cannot be completed due to data preparation issues.")

    def analyze(self):
        self.run_analysis()
