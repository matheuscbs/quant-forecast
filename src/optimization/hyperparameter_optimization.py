import logging
from abc import ABC, abstractmethod

import config
import dask.dataframe as dd
import numpy as np
import optuna
import pandas as pd
from dask.distributed import Client, TimeoutError
from optuna.pruners import MedianPruner
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from src.optimization.data_granularity_checker import DataGranularityChecker
from src.optimization.data_preparation import DataPreparation


class HyperparameterOptimization(ABC):
    @abstractmethod
    def optimize(self, data, future_periods):
        pass

class OptunaOptimization(HyperparameterOptimization):
    def __init__(self, model_params=None):
        self.model_params = model_params or {}
        self.best_model = None

    def _adjust_hyperparameters(self, trial, is_intraday):
        """Defines the search space for Prophet model hyperparameters."""
        base_params = {
            "changepoint_prior_scale": trial.suggest_float("changepoint_prior_scale", 0.01, 0.5),
            "changepoint_range": trial.suggest_float("changepoint_range", 0.8, 0.95),
            "holidays_prior_scale": trial.suggest_float("holidays_prior_scale", 10.0, 20.0),
        }
        if is_intraday:
            base_params["seasonality_prior_scale"] = trial.suggest_float("seasonality_prior_scale", 5.0, 15.0)
        else:
            base_params["seasonality_prior_scale"] = trial.suggest_float("seasonality_prior_scale", 10.0, 20.0)
        return base_params

    def _create_model(self, params, is_intraday):
        """Creates a Prophet model with the given hyperparameters."""
        model = Prophet(**params)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        if is_intraday:
            model.add_seasonality(name='hourly', period=24, fourier_order=8)
        else:
            model.add_seasonality(name='yearly', period=365.25, fourier_order=10)
        model.add_country_holidays(country_name=config.COUNTRY_NAME)
        return model

    def _evaluate_model(self, model, data, initial, period, horizon):
        """Evaluates the model using cross-validation and returns the mean MAPE."""
        try:
            # Assegurar que model.start é definido e não None
            if model.start is None:
                raise ValueError("Model start date is not defined.")

            # Filtra os dados históricos até a data de início do modelo
            history = data[data['ds'] <= model.start]
            if history.shape[0] < 2:
                raise ValueError('Less than two datapoints available to fit model.')

            df_cv = cross_validation(model, initial=initial, period=period, horizon=horizon, parallel="processes")
            df_p = performance_metrics(df_cv)
            return df_p['mape'].mean()

        except TimeoutError as e:
            logging.error(f"Timeout error while evaluating the model: {e}")
            return float('inf')
        except Exception as e:
            logging.error(f"Error evaluating the model: {e}")
            return float('inf')

    def objective(self, trial, data_splits, future_periods):
        """Objective function for Optuna optimization."""

        is_intraday = DataGranularityChecker.is_intraday(data_splits[0])
        hyperparameters = self._adjust_hyperparameters(trial, is_intraday)
        model = self._create_model(hyperparameters, is_intraday)

        results = []
        for data_split in data_splits:
            initial, period, horizon = DataPreparation.calculate_adaptive_parameters(
                data_split, future_periods, is_intraday
            )
            mape = self._evaluate_model(model, data_split, initial, period, horizon)
            results.append(mape)

        results = [np.float16(mape) for mape in results]
        mean_mape = np.mean(results)

        return mean_mape

    def optimize(self, data, future_periods, n_splits=5):
        """Optimizes Prophet model hyperparameters using Optuna, cross-validation, and Dask."""

        if not isinstance(data, pd.DataFrame) or 'ds' not in data.columns or 'y' not in data.columns:
            raise ValueError("Data must be a pandas DataFrame with 'ds' and 'y' columns.")

        logging.info("Starting hyperparameter optimization with %d-fold cross-validation...", n_splits)

        ddata = dd.from_pandas(data, npartitions=config.N_JOBS)
        data_splits = [split.compute() for split in ddata.random_split([1 / n_splits] * n_splits)]

        study = optuna.create_study(direction='minimize', pruner=MedianPruner())
        study.optimize(lambda trial: self.objective(trial, data_splits, future_periods), n_trials=config.N_TRIALS, n_jobs=1)

        logging.info(f"Hyperparameter optimization complete. Best parameters: {study.best_trial.params}")

        return study.best_params
