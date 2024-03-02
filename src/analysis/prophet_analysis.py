import logging

import matplotlib.pyplot as plt
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.plot import add_changepoints_to_plot, plot_cross_validation_metric

from src.data.data_fetcher import DataFetcher
from src.optimization.hyperparameter_optimization import OptunaOptimization

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProphetAnalysis:
    def __init__(self, ticker, period, future_periods, country_name='BR'):
        self.ticker = ticker
        self.period = period
        self.future_periods = future_periods
        self.country_name = country_name
        self.data_fetcher = DataFetcher()
        self.optuna_optimization = OptunaOptimization(country_name=country_name)
        self.model = None
        self.forecast = None

    def fetch_and_prepare_data(self):
        logging.info(f"Fetching and preparing data for {self.ticker}")
        data = self.data_fetcher.fetch_data(self.ticker, self.period)
        if data is not None:
            logging.info(f"Data for {self.ticker} prepared successfully.")
        else:
            logging.error(f"Failed to prepare data for {self.ticker}.")
            raise ValueError(f"Failed to fetch or prepare data for {self.ticker}.")
        return data

    def optimize_and_fit(self, data):
        logging.info(f"Starting hyperparameter optimization for {self.ticker}")
        self.optuna_optimization.optimize(data, self.future_periods)
        self.model = self.optuna_optimization.best_model
        logging.info(f"Model for {self.ticker} fitted successfully with best parameters.")

    def cross_validate_model(self):
        logging.info(f"Starting cross-validation for {self.ticker}")
        initial, period, horizon = self.optuna_optimization.calculate_adaptive_parameters(self.model.history, self.future_periods)
        df_cv = cross_validation(self.model, initial=initial, period=period, horizon=horizon)
        plot_cross_validation_metric(df_cv, metric='mape')
        plt.title(f"MAPE Metric for {self.ticker}")
        plt.savefig(f"mape_metric_{self.ticker}.png", dpi=300)
        plt.close()
        logging.info(f"Cross-validation for {self.ticker} completed.")

    def make_forecast(self):
        logging.info(f"Generating forecasts for {self.ticker}")
        future = self.model.make_future_dataframe(periods=self.future_periods)
        self.forecast = self.model.predict(future)

    def plot_forecast(self):
        fig = self.model.plot(self.forecast)
        add_changepoints_to_plot(fig.gca(), self.model, self.forecast)
        plt.title(f"Forecast and Changepoints for {self.ticker}")
        plt.savefig(f"forecast_{self.ticker}.png", dpi=300)
        plt.close()
        logging.info(f"Forecast plot for {self.ticker} saved.")

    def run_analysis(self):
        data = self.fetch_and_prepare_data()
        if data is not None:
            self.optimize_and_fit(data)
            self.cross_validate_model()
            self.make_forecast()
            self.plot_forecast()
        else:
            logging.error(f"Analysis for {self.ticker} cannot be completed due to data preparation issues.")
