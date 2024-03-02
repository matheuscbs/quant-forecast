import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from arch import arch_model
from scipy.optimize import differential_evolution


class IndicatorCalculator:
    def __init__(self, data):
        self.data = data

class VolatilityAnalysis(IndicatorCalculator):
    def analyze_garch(self):
        retornos = self.data['Retornos'].dropna() * 100
        modelo_garch = arch_model(retornos, vol='Garch', p=1, q=1, dist='Normal')
        resultado_garch = modelo_garch.fit(disp='off')
        previsao_volatilidade = resultado_garch.forecast(horizon=30, method='simulation')
        futura_volatilidade = previsao_volatilidade.variance.iloc[-1]
        return futura_volatilidade

class TechnicalIndicators(IndicatorCalculator):
    @staticmethod
    def calculate_RSI(data, column='y', period=14):
        delta = data[column].diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        data['RSI'] = rsi
        return data

    @staticmethod
    def calculate_EMA(data, column='y', period=21):
        ema = data[column].ewm(span=period, adjust=False).mean()
        data[f'EMA_{period}'] = ema
        return data

    @staticmethod
    def calculate_HiLo(data, period=14, column='y'):
        data['HiLo_High'] = data[column].rolling(window=period).max()
        data['HiLo_Low'] = data[column].rolling(window=period).min()
        return data

class StrategyEvaluator:
    @staticmethod
    def hilo_activator(highs, lows, period):
        hilo_long = highs.rolling(window=period).max()
        hilo_short = lows.rolling(window=period).min()
        return hilo_long, hilo_short

    @staticmethod
    def evaluate_strategy(parameters, price_data):
        period = int(parameters[0])
        hilo_long, hilo_short = StrategyEvaluator.hilo_activator(price_data['High'], price_data['Low'], period)

        price_data['Signal'] = 0
        price_data.loc[price_data['Close'] > hilo_long.shift(1), 'Signal'] = 1
        price_data.loc[price_data['Close'] < hilo_short.shift(1), 'Signal'] = -1

        price_data['Strategy_Returns'] = price_data['Signal'].shift(1) * price_data['Close'].pct_change()
        return -price_data['Strategy_Returns'].cumsum().iloc[-1]

    @staticmethod
    def optimize_strategy(price_data, bounds):
        result = differential_evolution(StrategyEvaluator.evaluate_strategy, bounds, args=(price_data,))
        return result.x, -result.fun
