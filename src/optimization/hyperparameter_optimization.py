import logging
from abc import ABC, abstractmethod

import config
import optuna
import pandas as pd
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
    def __init__(self, n_trials=config.N_TRIALS, n_jobs=config.N_JOBS, country_name='BR', model_params=None):
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.country_name = country_name
        self.model_params = model_params or {}
        self.best_model = None
        self.is_intraday = False

    def _adjust_hyperparameters(self, trial, is_intraday):
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
        model = Prophet(**params)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        if is_intraday:
            model.add_seasonality(name='hourly', period=24, fourier_order=8)
        else:
            model.add_seasonality(name='yearly', period=365.25, fourier_order=10)
        model.add_country_holidays(country_name=self.country_name)
        return model

    def objective(self, trial, data, future_periods):
        is_intraday = DataGranularityChecker.is_intraday(data)
        hyperparameters = self._adjust_hyperparameters(trial, is_intraday)
        model = self._create_model(hyperparameters, is_intraday)
        model.fit(data)

        initial_str, period_str, horizon_str = DataPreparation.calculate_adaptive_parameters(data, future_periods, is_intraday)
        df_cv = cross_validation(model, initial=initial_str, period=period_str, horizon=horizon_str)
        df_p = performance_metrics(df_cv)
        return df_p['mape'].mean()

    def optimize(self, data, future_periods):
        if not isinstance(data, pd.DataFrame) or 'ds' not in data.columns or 'y' not in data.columns:
            raise ValueError("Data must be a pandas DataFrame with 'ds' and 'y' columns.")

        logging.info("Iniciando a otimização de hiperparâmetros...")
        study = optuna.create_study(direction='minimize', pruner=MedianPruner())
        study.optimize(lambda trial: self.objective(trial, data, future_periods), n_trials=self.n_trials, n_jobs=self.n_jobs)

        logging.info(f"Otimização de hiperparâmetros concluída. Melhores parâmetros: {study.best_trial.params}")
        best_params = study.best_trial.params
        is_intraday = DataGranularityChecker.is_intraday(data)
        self.best_model = self._create_model(best_params, is_intraday)
        self.best_model.fit(data)

        return best_params

    def _logging_callback(self, study, trial):
        trial_value = trial.value if trial.value is not None else 'None'
        logging.info(f"Trial {trial.number} finished with value: {trial_value} and parameters: {trial.params}.")
        if study.best_trial == trial:
            logging.info(f"New best trial! Value: {trial_value}, Params: {trial.params}")
