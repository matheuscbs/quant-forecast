import os

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import yfinance as yf
from prophet.plot import add_changepoints_to_plot, plot_cross_validation_metric
from src.analysis.strategy_evaluator import StrategyEvaluator


class Plotter:
    @staticmethod
    def plot_last_days_forecast(data, forecast, future_periods, ticker, historical_periods=-30):
        historical_data = data.tail(-historical_periods)
        last_historical_point = historical_data.iloc[-1]
        forecast_start = forecast[forecast['ds'] == last_historical_point['ds']]
        if not forecast_start.empty:
            gap = last_historical_point['y'] - forecast_start['yhat'].values[0]
            forecast['yhat'] += gap
            forecast['yhat_upper'] += gap
            forecast['yhat_lower'] += gap

        plt.figure(figsize=(10, 6))
        plt.plot(historical_data['ds'], historical_data['y'], label='Dados Históricos', color='black')
        plt.plot(forecast['ds'], forecast['yhat'], label='Previsão', color='blue')
        plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.5, label='Margem de Erro')

        plt.title(f'Últimos {abs(historical_periods)} Dias e Previsão Futura - {ticker}')
        plt.xlabel('Data')
        plt.ylabel('Preço')
        plt.legend()
        plt.tight_layout()

        plt.savefig(f"last_days_forecast_{ticker}.png")
        plt.close()

    def plot_prophet_forecast(self, ticker, model, forecast):
        plt.figure(figsize=(15, 8))
        fig = model.plot(forecast)
        add_changepoints_to_plot(fig.gca(), model, forecast)
        plt.title(f"Price Forecast for {ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend(loc='upper left')
        plt.savefig(f"forecast_{ticker}.png", bbox_inches='tight')
        plt.close()

    @staticmethod
    def plot_components(ticker, model, forecast):
        model.plot_components(forecast)
        plt.suptitle(f"Forecast Components - {ticker}")
        plt.savefig(f"components_{ticker}.png", bbox_inches='tight', dpi=300)
        plt.close()

    @staticmethod
    def plot_hilo_strategy(price_data, best_period, ticker):
        hilo_long, hilo_short = StrategyEvaluator.hilo_activator(price_data['High'], price_data['Low'], int(best_period))
        price_data['HiLo_Long'] = hilo_long
        price_data['HiLo_Short'] = hilo_short
        plt.figure(figsize=(14, 7))
        plt.plot(price_data.index, price_data['Close'], label='Close Price', color='black')
        plt.plot(price_data.index, price_data['HiLo_Long'], label='HiLo Long', color='green', linestyle='--')
        plt.plot(price_data.index, price_data['HiLo_Short'], label='HiLo Short', color='red', linestyle='--')
        buy_signals = price_data['Close'] > price_data['HiLo_Long']
        sell_signals = price_data['Close'] < price_data['HiLo_Short']
        plt.plot(price_data[buy_signals].index, price_data['Close'][buy_signals], '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(price_data[sell_signals].index, price_data['Close'][sell_signals], 'v', markersize=10, color='r', label='Sell Signal')

        plt.title(f"HiLo Activator Strategy for {ticker} - Best Period: {best_period} Days")
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.savefig(f"HiLo_Strategy_{ticker}.png")
        plt.close()

    @staticmethod
    def plot_correlation(prices, title='Stock Correlation Matrix'):
        """
        Plota a matriz de correlação dos retornos dos ativos.

        :param prices: DataFrame com os preços de fechamento ajustados dos ativos.
        :param title: Título do gráfico.
        """
        correlation = prices.pct_change().corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title(title)
        plt.savefig("correlation_matrix.png")
        plt.close()

    @staticmethod
    def plot_with_indicators(data, last_days=60):
        ohlc_data = data[-last_days:].copy()
        ohlc_data.set_index('ds', inplace=True)
        ohlc_data.index = pd.DatetimeIndex(ohlc_data.index)

        apds = [
            mpf.make_addplot(ohlc_data['EMA_21'], color='blue'),
            mpf.make_addplot(ohlc_data['HiLo_High'], color='green', linestyle='dashdot'),
            mpf.make_addplot(ohlc_data['HiLo_Low'], color='red', linestyle='dashdot'),
            mpf.make_addplot(ohlc_data['RSI'], panel=1, color='purple', ylabel='RSI')
        ]

        overbought_line = [70] * len(ohlc_data)
        oversold_line = [30] * len(ohlc_data)
        apds.append(mpf.make_addplot(overbought_line, panel=1, color='red', linestyle='--'))
        apds.append(mpf.make_addplot(oversold_line, panel=1, color='green', linestyle='--'))

        mpf.plot(ohlc_data, type='candle', addplot=apds, volume=True, figratio=(12, 8), style='charles',
                 title="Candlestick with EMA, HiLo, and RSI", panel_ratios=(6, 1))

        plt.savefig(f"candlestick_RSI_{last_days}_days.png")
        plt.close()

    @staticmethod
    def plot_garch_volatility(futura_volatilidade, filename="volatilidade_garch.png"):
        plt.figure(figsize=(10, 6))
        futura_volatilidade.plot(title='Previsão de Volatilidade - Modelo GARCH')
        plt.xlabel('Dias Futuros')
        plt.ylabel('Volatilidade (%)')
        plt.legend(['Volatilidade Prevista'])
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def plot_cross_validation_metric(df_cv, metric, title):
        plot_cross_validation_metric(df_cv, metric=metric)
        plt.title(title)
        plt.savefig(f"{metric}_metric.png", dpi=300)
        plt.close()
