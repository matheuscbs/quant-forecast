import logging
from abc import ABC, abstractmethod

import optuna
import pandas as pd
from optuna.pruners import MedianPruner
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from src.data.data_preparation import DataPreparation


class HyperparameterOptimization(ABC):
    @abstractmethod
    def optimize(self, data, future_periods):
        pass

class OptunaOptimization(HyperparameterOptimization):
    def __init__(self, n_trials=1, n_jobs=1, country_name='BR', model_params=None):
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.country_name = country_name
        self.model_params = model_params or {}
        self.best_model = None

    def objective(self, trial, data, future_periods):
        params = self.model_params.copy()
        params.update({
            "changepoint_prior_scale": trial.suggest_float("changepoint_prior_scale", 0.01, 0.5),
            "changepoint_range": trial.suggest_float("changepoint_range", 0.8, 0.95),
            "seasonality_prior_scale": trial.suggest_float("seasonality_prior_scale", 10.0, 20.0),
            "holidays_prior_scale": trial.suggest_float("holidays_prior_scale", 10.0, 20.0),
        })
        model = Prophet(**params)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        model.add_country_holidays(country_name=self.country_name)
        model.fit(data)

        initial_str, period_str, horizon_str = DataPreparation.calculate_adaptive_parameters(data, future_periods)
        df_cv = cross_validation(model, initial=initial_str, period=period_str, horizon=horizon_str)
        df_p = performance_metrics(df_cv)
        return df_p['mape'].mean()

    def optimize(self, data, future_periods):
        if not isinstance(data, pd.DataFrame) or 'ds' not in data or 'y' not in data:
            raise ValueError("Data must be a pandas DataFrame with 'ds' and 'y' columns.")

        logging.info("Iniciando a otimização de hiperparâmetros...")
        study = optuna.create_study(direction='minimize', pruner=MedianPruner())
        study.optimize(lambda trial: self.objective(trial, data, future_periods), n_trials=self.n_trials, n_jobs=self.n_jobs)

        logging.info(f"Otimização de hiperparâmetros concluída. Melhores parâmetros: {study.best_trial.params}")

        best_params = study.best_trial.params
        self.best_model = Prophet(**best_params)
        self.best_model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        self.best_model.add_country_holidays(country_name=self.country_name)
        self.best_model.fit(data)

        return best_params

    def _logging_callback(self, study, trial):
        trial_value = trial.value if trial.value is not None else 'None'
        logging.info(f"Trial {trial.number} finished with value: {trial_value} and parameters: {trial.params}.")
        if study.best_trial == trial:
            logging.info(f"New best trial! Value: {trial_value}, Params: {trial.params}")
