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
    def __init__(self, n_trials=config.N_TRIALS, n_jobs=config.N_JOBS, country_name='BR', model_params=None):
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.country_name = country_name
        self.model_params = model_params or {}
        self.best_model = None
        self.is_intraday = False

    def _adjust_hyperparameters(self, trial, is_intraday):
        """
        Define o espaço de busca para os hiperparâmetros do modelo Prophet.
        """
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
        """
        Cria um modelo Prophet com os hiperparâmetros fornecidos.
        """
        model = Prophet(**params)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=7)
        if is_intraday:
            model.add_seasonality(name='hourly', period=24, fourier_order=8)
        else:
            model.add_seasonality(name='yearly', period=365.25, fourier_order=10)
        model.add_country_holidays(country_name=self.country_name)
        return model

    def _evaluate_model(self, model, data, initial, period, horizon):
        """
        Avalia o modelo usando validação cruzada e retorna o MAPE médio.
        """
        try:
            df_cv = cross_validation(model, initial=initial, period=period, horizon=horizon)
            df_p = performance_metrics(df_cv)
            return df_p['mape'].mean()
        except TimeoutError as e:
            logging.error(f"Erro de tempo limite ao avaliar o modelo: {e}")
            return float('inf')
        except Exception as e:
            logging.error(f"Erro ao avaliar o modelo: {e}")
            return float('inf')

    def objective(self, trial, data_splits, future_periods):
        """
        Função objetivo para a otimização com Optuna.
        """
        is_intraday = DataGranularityChecker.is_intraday(data_splits[0].compute())
        hyperparameters = self._adjust_hyperparameters(trial, is_intraday)
        model = self._create_model(hyperparameters, is_intraday)

        results = []
        for data_split in data_splits:
            initial, period, horizon = DataPreparation.calculate_adaptive_parameters(
                data_split.compute(), future_periods, is_intraday
            )
            mape = self._evaluate_model(model, data_split, initial, period, horizon)
            results.append(mape)

        # Ajuste de precisão para float16
        results = [np.float16(mape) for mape in results]
        mean_mape = np.mean(results)

        return mean_mape

    def optimize(self, data, future_periods, n_splits=5):
        """
        Otimiza os hiperparâmetros do modelo Prophet usando Optuna, validação cruzada e Dask para big data.
        """

        if not isinstance(data, pd.DataFrame) or 'ds' not in data.columns or 'y' not in data.columns:
            raise ValueError("Data must be a pandas DataFrame with 'ds' and 'y' columns.")

        logging.info("Iniciando a otimização de hiperparâmetros com validação cruzada em %d partes...", n_splits)

        # Converte o DataFrame Pandas para Dask DataFrame
        ddata = dd.from_pandas(data, npartitions=self.n_jobs)

        # Divide os dados em n_splits partes para validação cruzada
        data_splits = ddata.random_split([1 / n_splits] * n_splits)

        # Inicia o cliente Dask para processamento distribuído
        client = Client()

        study = optuna.create_study(direction='minimize', pruner=MedianPruner())
        study.optimize(lambda trial: self.objective(trial, data_splits, future_periods),
                       n_trials=self.n_trials, n_jobs=1)

        client.close()  # Fecha o cliente Dask

        logging.info(f"Otimização de hiperparâmetros concluída. Melhores parâmetros: {study.best_trial.params}")
        best_params = study.best_trial.params
        is_intraday = DataGranularityChecker.is_intraday(data)
        self.best_model = self._create_model(best_params, is_intraday)
        self.best_model.fit(data)  # Treina o modelo final com todos os dados

        return best_params
