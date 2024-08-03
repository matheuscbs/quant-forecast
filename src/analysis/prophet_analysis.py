import logging

import pandas as pd
from config import COUNTRY_NAME
from dask.dataframe import DataFrame as DaskDataFrame
from dask.distributed import Client
from prophet import Prophet
from prophet.diagnostics import cross_validation
from src.analysis.i_analysis import IAnalysis
from src.optimization.data_granularity_checker import DataGranularityChecker
from src.optimization.data_preparation import DataPreparation
from src.optimization.hyperparameter_optimization import OptunaOptimization

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProphetAnalysis(IAnalysis):
    def __init__(self, ticker, data, future_periods, client=None):
        self.ticker = ticker
        self.data = data
        self.future_periods = future_periods
        self.optuna_optimization = OptunaOptimization()
        self.model = None
        self.forecast = None
        self.client = client or Client()
        self.is_intraday = DataGranularityChecker.is_intraday(data)

    def optimize_and_fit(self):
        if not isinstance(self.data, pd.DataFrame) or self.data.empty:
            logging.error("No valid data provided for optimization and fitting.")
            return

        if 'ds' not in self.data.columns or 'y' not in self.data.columns:
            logging.error("Dataframe must contain 'ds' and 'y' columns.")
            return

        logging.info("Starting hyperparameter optimization and model fitting")
        best_params = self.optuna_optimization.optimize(self.data, self.future_periods)
        logging.info(f"Best hyperparameters: {best_params}")
        self.model = Prophet(**best_params)
        self.model.add_country_holidays(country_name=COUNTRY_NAME)

        try:
            self.model.fit(self.data)
            # Define manualmente a data de início com a menor data 'ds' no conjunto de dados
            self.model.start = self.data['ds'].min()
            logging.info("Model fitting completed successfully")
        except Exception as e:
            logging.error(f"Error fitting the model: {e}")
            self.model = None

    def cross_validate_model(self):
        if not self.model:
            logging.error("Model is not fitted yet.")
            return None

        logging.info("Starting cross-validation")
        try:
            initial, period, horizon = DataPreparation.calculate_adaptive_parameters(
                self.data, self.future_periods, self.is_intraday
            )
            df_cv = cross_validation(
                self.model, initial=initial, period=period, horizon=horizon, parallel="processes"
            )
            logging.info("Cross-validation completed successfully")
            return df_cv
        except Exception as e:
            logging.error(f"Error during cross-validation: {e}")
            return None

    def make_forecast(self):
        if not self.model:
            logging.error("Model is not prepared to make forecasts.")
            return None

        logging.info("Generating forecasts")
        try:
            future = self.model.make_future_dataframe(periods=self.future_periods)
            self.forecast = self.model.predict(future)
            logging.info("Forecast generation completed successfully")
            return self.forecast
        except Exception as e:
            logging.error(f"Error during forecast generation: {e}")
            return None

    def run_analysis(self):
        if not isinstance(self.data, pd.DataFrame) or self.data.empty:
            logging.error("Data is not prepared properly for analysis.")
            return None, None, None

        self.optimize_and_fit()
        df_cv = self.cross_validate_model() if self.model else None
        forecast = self.make_forecast() if self.model else None
        return self.model, forecast, df_cv

    def analyze(self):
        return self.run_analysis()
