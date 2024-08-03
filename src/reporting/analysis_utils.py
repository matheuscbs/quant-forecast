import logging
import os

import pandas as pd
from src.analysis.indicator_calculator import IndicatorCalculator
from src.analysis.prophet_analysis import ProphetAnalysis
from src.analysis.strategy_evaluator import StrategyEvaluator
from src.analysis.volatility_analysis import VolatilityAnalysis


class AnalysisGenerator:
    def __init__(self, function, required_args, title, description):
        self.function = function
        self.required_args = required_args
        self.title = title
        self.description = description

    def generate(self, **kwargs):
        filtered_kwargs = {arg: kwargs[arg] for arg in self.required_args if arg in kwargs}
        try:
            return self.function(**filtered_kwargs)
        except Exception as e:
            logging.error(f"Error generating {self.title} analysis: {e}")
            return None, None, []

    def _generate_title_description_filenames(self, title, description, filenames):
        if title and description and filenames:
            return title, description, filenames
        else:
            logging.error(f"Falha ao gerar análise {self.title}.")
            return None, None, []

    def _handle_errors(self, e):
        logging.error(f"Erro ao gerar análise {self.title}: {e}")
        return None, None, []


def generate_prophet_analysis(plotter, ticker, data, future_periods=15, client=None):
    prophet = ProphetAnalysis(ticker, data, future_periods, client=client)
    model, forecast, df_cv = prophet.analyze()

    if model is not None and not forecast.empty:
        filenames = [plotter.plot_prophet_forecast(ticker, model, forecast)]
        if df_cv is not None:
            filenames.extend([
                plotter.plot_components(ticker, model, forecast),
                plotter.plot_cross_validation_metric(df_cv, metric="rmse", title="RMSE Metric", ticker=ticker),
                plotter.plot_last_days_forecast(data, forecast, future_periods, ticker, plotter.last_days),
            ])
        else:
            logging.warning("Não foi possível realizar a validação cruzada. Pulando plotagem das métricas.")

        return 'Análise de Séries Temporais com Prophet', "Análise de Séries Temporais com Prophet", filenames
    else:
        logging.error("Falha ao gerar análise do Prophet.")
        return None, None, []

def generate_indicator_calculator(plotter, data, **kwargs):
    logging.info("Generating statistical analysis")
    if not isinstance(data, pd.DataFrame):
        logging.warning("'data' não é um DataFrame. Tentando converter...")
        try:
            data = pd.DataFrame(data)
        except Exception as e:
            logging.error(f"Não foi possível converter 'data' para DataFrame: {e}")
            return None, None, []

    data = IndicatorCalculator.calculate_RSI(data, period=14)
    data = IndicatorCalculator.calculate_EMA(data, period=21)
    data = IndicatorCalculator.calculate_HiLo(data, period=14)

    description = "Analysis with RSI, EMA, and HiLo indicators."
    title = 'Análise Estatística'
    filenames = [plotter.plot_with_indicators(data, plotter.last_days)]
    return title, description, filenames

def generate_strategy_evaluator(plotter, ticker, data, **kwargs):
    logging.info("Generating strategy evaluation")

    if 'ds' in data.columns:
        data.set_index('ds', inplace=True)
    elif 'Date' in data.columns:
        data.set_index('Date', inplace=True)
    data.index = pd.to_datetime(data.index, errors='coerce')

    if data.index.isnull().any():
        logging.error("Falha na conversão do índice para DatetimeIndex após tentativas de correção.")
        return None, None, []

    price_data = data[['High', 'Low', 'Close']].copy()

    bounds = [(1, 100)]
    best_period, best_score = StrategyEvaluator.optimize_strategy(price_data, bounds)
    hilo_long, hilo_short = StrategyEvaluator.hilo_activator(price_data['High'], price_data['Low'], int(best_period))

    descriptions = f"Melhor período para HiLo Activator: {best_period} dias, Resultado da Estratégia: {best_score:.2f}"
    titles = 'Avaliação da Estratégia HiLo Activator'
    filenames = [plotter.plot_hilo_strategy(price_data, best_period, ticker, hilo_long, hilo_short)]

    return titles, descriptions, filenames

def generate_volatility_analysis(plotter, data, models=['GARCH', 'EGARCH', 'GJR-GARCH'], horizon=30):
    logging.info("Generating volatility analysis")
    volatility_analysis = VolatilityAnalysis(data['Retornos'])
    future_volatility = volatility_analysis.analyze(models=models, horizon=horizon)

    descriptions = []
    titles = []
    filenames = []

    for model_name, vol in future_volatility.items():
        descriptions.append(f"Modelo: {model_name}, Futura Volatilidade: {vol.iloc[-1].item():.2f}%")
        titles.append(f'Análise de Volatilidade - {model_name}')
        filenames.append(plotter.plot_garch_volatility(vol, title=titles[-1]))

    return titles, descriptions, filenames
