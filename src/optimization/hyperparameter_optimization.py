import logging
from abc import ABC, abstractmethod

import optuna
import pandas as pd
from optuna.pruners import MedianPruner
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from src.data.data_preparation import DataPreparation


class HyperparameterOptimization(ABC):
    """
    Interface para otimização de hiperparâmetros.
    """
    @abstractmethod
    def optimize(self, data, future_periods):
        """
        Deve ser implementado para realizar a otimização de hiperparâmetros.

        Args:
            data (pd.DataFrame): DataFrame contendo as colunas 'ds' e 'y'.
            future_periods (int): Número de períodos para previsão futura.

        Returns:
            dict: Melhores hiperparâmetros encontrados.
        """
        pass

class OptunaOptimization(HyperparameterOptimization):
    """
    Otimização de hiperparâmetros com Optuna para modelos Prophet.
    """
    def __init__(self, n_trials=30, n_jobs=1, country_name='BR'):
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.best_params = None
        self.best_model = None
        self.country_name = country_name

    def objective(self, trial, data, future_periods, country_name='BR'):
        params = {
            "changepoint_prior_scale": trial.suggest_float("changepoint_prior_scale", 0.01, 0.5),
            "changepoint_range": trial.suggest_float("changepoint_range", 0.8, 0.95),
            "seasonality_prior_scale": trial.suggest_float("seasonality_prior_scale", 10.0, 20.0),
            "holidays_prior_scale": trial.suggest_float("holidays_prior_scale", 10.0, 20.0),
        }
        model = Prophet(**params)

        model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        model.add_country_holidays(country_name=country_name)
        model.fit(data)

        initial_str, period_str, horizon_str = DataPreparation.calculate_adaptive_parameters(data, future_periods)
        df_cv = cross_validation(model, initial=initial_str, period=period_str, horizon=horizon_str)
        df_p = performance_metrics(df_cv)
        mape = df_p['mape'].mean()

        return mape

    def optimize(self, data, future_periods):
        if not isinstance(data, pd.DataFrame) or 'ds' not in data or 'y' not in data:
            raise ValueError("Data must be a pandas DataFrame with 'ds' and 'y' columns.")

        logging.info("Iniciando a otimização de hiperparâmetros...")
        pruner = MedianPruner()

        study = optuna.create_study(direction='minimize', pruner=pruner)
        study.optimize(lambda trial: self.objective(trial, data, future_periods), n_trials=30, n_jobs=1)

        self.best_params = study.best_trial.params
        logging.info(f"Otimização de hiperparâmetros concluída. Melhores parâmetros: {study.best_trial.params}")

        self.best_model = Prophet(**self.best_params)
        self.best_model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        self.best_model.add_country_holidays(country_name='BR')
        self.best_model.fit(data)

        return self.best_params

    def _logging_callback(self, study, trial):
        trial_value = trial.value if trial.value is not None else 'None'
        logging.info(f"Trial {trial.number} finished with value: {trial_value} and parameters: {trial.params}.")
        logging.info(f"Best is trial {study.best_trial.number} with value: {study.best_trial.value}.")

        return self.best_params
