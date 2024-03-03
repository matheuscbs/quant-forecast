import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import yfinance as yf
from prophet.plot import add_changepoints_to_plot, plot_cross_validation_metric


class Plotter:
    def __init__(self):
        self.image_path = "/app/relatorios/images/"

    def plot_last_days_forecast(self, data, forecast, future_periods, ticker, historical_periods=30):
        historical_data = data.tail(historical_periods)
        last_historical_point = historical_data.iloc[-1]
        forecast['gap'] = forecast['yhat'].shift(-1) - forecast['yhat']
        forecast_start_index = forecast[forecast['ds'] >= last_historical_point['ds']].index[0]

        gap = last_historical_point['y'] - forecast.at[forecast_start_index, 'yhat']

        forecast.loc[forecast_start_index:, 'yhat'] += gap
        forecast.loc[forecast_start_index:, 'yhat_upper'] += gap
        forecast.loc[forecast_start_index:, 'yhat_lower'] += gap

        future_data = forecast.loc[forecast_start_index:forecast_start_index + future_periods]

        plt.figure(figsize=(10, 6))

        plt.plot(historical_data['ds'], historical_data['y'], label='Dados Históricos', color='black')
        plt.plot(future_data['ds'], future_data['yhat'], label='Previsão', color='blue')
        plt.fill_between(future_data['ds'], future_data['yhat_lower'], future_data['yhat_upper'], color='gray', alpha=0.5, label='Margem de Erro')

        plt.title(f'Últimos {historical_periods} Dias e Previsão Futura - {ticker}')
        plt.xlabel('Data')
        plt.ylabel('Preço')
        plt.legend()
        plt.tight_layout()

        plt.savefig(os.path.join(self.image_path, f"last_days_forecast_{ticker}.png"))
        plt.close()
        return f"last_days_forecast_{ticker}.png"

    def plot_prophet_forecast(self, ticker, model, forecast):
        plt.figure(figsize=(15, 8))
        fig = model.plot(forecast)
        add_changepoints_to_plot(fig.gca(), model, forecast)
        plt.title(f"Price Forecast for {ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend(loc='upper left')
        plt.savefig(os.path.join(self.image_path, f"forecast_{ticker}.png"), bbox_inches='tight')
        plt.close()
        return f"forecast_{ticker}.png"

    def plot_components(self, ticker, model, forecast):
        model.plot_components(forecast)
        plt.suptitle(f"Forecast Components - {ticker}")
        plt.savefig(os.path.join(self.image_path, f"components_{ticker}.png"), bbox_inches='tight', dpi=300)
        plt.close()
        return f"components_{ticker}.png"

    def plot_hilo_strategy(self, price_data, best_period, ticker, hilo_long, hilo_short):
        if 'Date' not in price_data.columns:
            price_data['Date'] = price_data.index

        price_data['HiLo_Long'] = hilo_long
        price_data['HiLo_Short'] = hilo_short

        plt.figure(figsize=(14, 7))
        plt.plot(price_data['Date'], price_data['Close'], label='Close Price', color='black')
        plt.plot(price_data['Date'], price_data['HiLo_Long'], label='HiLo Long', color='green', linestyle='--')
        plt.plot(price_data['Date'], price_data['HiLo_Short'], label='HiLo Short', color='red', linestyle='--')

        buy_signals = price_data['Close'] > price_data['HiLo_Long']
        sell_signals = price_data['Close'] < price_data['HiLo_Short']

        plt.plot(price_data.loc[buy_signals, 'Date'], price_data.loc[buy_signals, 'Close'], '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(price_data.loc[sell_signals, 'Date'], price_data.loc[sell_signals, 'Close'], 'v', markersize=10, color='r', label='Sell Signal')

        plt.title(f"HiLo Activator Strategy for {ticker} - Best Period: {best_period} Days")
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()

        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
        plt.gcf().autofmt_xdate()

        plt.savefig(os.path.join(self.image_path, f"HiLo_Strategy_{ticker}.png"))
        plt.close()
        return f"HiLo_Strategy_{ticker}.png"

    def plot_correlation(self, prices, title='Stock Correlation Matrix'):
        """
        Plota a matriz de correlação dos retornos dos ativos.

        :param prices: DataFrame com os preços de fechamento ajustados dos ativos.
        :param title: Título do gráfico.
        """
        correlation = prices.pct_change().corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title(title)
        plt.savefig(os.path.join(self.image_path, "correlation_matrix.png"))
        plt.close()
        return "correlation_matrix.png"

    def plot_with_indicators(self, data, last_days=60):
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

        mpf.plot(ohlc_data, type='candle', addplot=apds, volume='Volume' in ohlc_data.columns, figratio=(12, 8), style='charles',
                 title="Candlestick with EMA, HiLo, and RSI", panel_ratios=(6, 1))

        plt.savefig(os.path.join(self.image_path, f"candlestick_RSI_{last_days}_days.png"))
        plt.close()
        return f"candlestick_RSI_{last_days}_days.png"

    def plot_garch_volatility(self, futura_volatilidade, filename="volatilidade_garch.png"):
        plt.figure(figsize=(10, 6))
        futura_volatilidade.plot(title='Previsão de Volatilidade - Modelo GARCH')
        plt.xlabel('Dias Futuros')
        plt.ylabel('Volatilidade (%)')
        plt.legend(['Volatilidade Prevista'])
        plt.savefig(os.path.join(self.image_path, filename))
        plt.close()
        return filename

    def plot_cross_validation_metric(self, df_cv, metric, title, ticker):
        plot_cross_validation_metric(df_cv, metric=metric)
        plt.title(title)
        plt.savefig(os.path.join(self.image_path, f"{metric}_metric_{ticker}.png"), dpi=300)
        plt.close()
        return f"{metric}_metric_{ticker}.png"
