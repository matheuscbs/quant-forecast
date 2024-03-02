import os

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import yfinance as yf
from prophet.plot import add_changepoints_to_plot


class Plotter:
    @staticmethod
    def plot_last_days_forecast(data, forecast, future_periods, ticker, historical_periods=-30):
        historical_periods = data[historical_periods:]
        last_historical_point = historical_periods.iloc[-1]

        forecast_start = forecast[forecast['ds'] == last_historical_point['ds']]
        if not forecast_start.empty:
            gap = last_historical_point['y'] - forecast_start['yhat'].values[0]
            forecast['yhat'] += gap
            forecast['yhat_upper'] += gap
            forecast['yhat_lower'] += gap

        complete_forecast = forecast[forecast['ds'] >= last_historical_point['ds']]

        plt.figure(figsize=(10, 6))
        plt.plot(historical_periods['ds'], historical_periods['y'], label='Historical Data')
        plt.plot(complete_forecast['ds'], complete_forecast['yhat'], label='Forecast', color='blue')
        plt.fill_between(complete_forecast['ds'], complete_forecast['yhat_lower'], complete_forecast['yhat_upper'], color='gray', alpha=0.5, label='Error Margin')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Last 30 Days and Future Forecast - {ticker}')
        plt.legend()
        plt.savefig(f"last_days_forecast_{ticker}.png")
        plt.close()

    @staticmethod
    def plot_forecast(ticker, model, forecast):
        plt.figure(figsize=(15, 8))
        fig = model.plot(forecast)
        add_changepoints_to_plot(fig.gca(), model, forecast)
        plt.title(f"Price Forecast - {ticker}")
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
    def plot_correlation(assets, period='5y'):
        prices = pd.DataFrame()
        for asset in assets:
            prices[asset] = yf.download(asset, period=period)['Adj Close']
        correlation = prices.pct_change().corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Stock Correlation Matrix')
        plt.savefig("correlation_matrix.png")
        plt.close()
        return correlation

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
