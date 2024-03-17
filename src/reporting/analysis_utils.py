import logging

import pandas as pd
from src.analysis.indicator_calculator import IndicatorCalculator
from src.analysis.prophet_analysis import ProphetAnalysis
from src.analysis.strategy_evaluator import StrategyEvaluator
from src.analysis.volatility_analysis import VolatilityAnalysis


def generate_prophet_analysis(plotter, ticker, data, **kwargs):
    logging.info("Gerando análise do Prophet")
    future_periods = kwargs.get('future_periods', 15)
    prophet = ProphetAnalysis(ticker, data, future_periods)
    model, forecast, df_cv = prophet.analyze()

    if model is not None and not forecast.empty:
        description = "Análise de Séries Temporais com Prophet"
        title = 'Análise de Séries Temporais com Prophet'
        filenames = [
            plotter.plot_prophet_forecast(ticker, model, forecast),
            plotter.plot_components(ticker, model, forecast),
            plotter.plot_cross_validation_metric(df_cv, metric="mape", title="MAPE Metric", ticker=ticker),
            plotter.plot_last_days_forecast(data, forecast, future_periods, ticker, plotter.last_days)
        ]
        return title, description, filenames
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
    data = IndicatorCalculator.calculate_RSI(data, 'Close')
    data = IndicatorCalculator.calculate_EMA(data, 'Close')
    data = IndicatorCalculator.calculate_HiLo(data, 'High', 'Low')
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

def generate_volatility_analysis(plotter, data, **kwargs):
    logging.info("Generating volatility analysis")
    volatility_analysis = VolatilityAnalysis(data['Retornos'])
    future_volatility = volatility_analysis.analyze()

    descriptions = f"Futura Volatilidade: {future_volatility.iloc[-1].item():.2f}%"
    titles = 'Análise de Volatilidade'
    filenames = [plotter.plot_garch_volatility(future_volatility)]

    return titles, descriptions, filenames
