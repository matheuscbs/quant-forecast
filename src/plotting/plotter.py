import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import seaborn as sns
import yfinance as yf
from prophet.plot import add_changepoints_to_plot, plot_cross_validation_metric


class Plotter:
    def __init__(self, ticker, last_days=None, future_periods=None):
        self.image_path = "/app/relatorios/images/"
        self.ticker = ticker
        self.last_days = last_days
        self.future_periods = future_periods
        self.filenames = self.generate_filenames()

    def generate_filenames(self):
        return {
            "last_days_forecast": f"last_days_forecast_{self.ticker}.png",
            "forecast": f"forecast_{self.ticker}.png",
            "components": f"components_{self.ticker}.png",
            "HiLo_Strategy": f"HiLo_Strategy_{self.ticker}.png",
            "correlation_matrix": f"correlation_matrix_{self.ticker}.png",
            "candlestick_RSI": f"candlestick_RSI_{self.last_days}_days_{self.ticker}.png" if self.last_days else f"candlestick_RSI_{self.ticker}.png",
            "volatility": f"volatility_{self.ticker}.png",
            "metric": f"metric_{self.ticker}.png"
        }

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

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(historical_data['ds'], historical_data['y'], label='Dados Históricos', color='black')
        ax.plot(future_data['ds'], future_data['yhat'], label='Previsão', color='blue')
        ax.fill_between(future_data['ds'], future_data['yhat_lower'], future_data['yhat_upper'], color='gray', alpha=0.5, label='Margem de Erro')
        ax.set_title(f'Últimos {historical_periods} Dias e Previsão Futura - {ticker}')
        ax.set_xlabel('Data')
        ax.set_ylabel('Preço')
        ax.legend()
        plt.tight_layout()
        fig.savefig(os.path.join(self.image_path, self.filenames["last_days_forecast"]))
        plt.close(fig)
        return self.filenames["last_days_forecast"]

    def plot_prophet_forecast(self, ticker, model, forecast):
        fig, ax = plt.subplots(figsize=(15, 8))
        fig = model.plot(forecast, ax=ax)
        add_changepoints_to_plot(fig.gca(), model, forecast)
        ax.set_title(f"Price Forecast for {ticker}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        fig.savefig(os.path.join(self.image_path, self.filenames["forecast"]), bbox_inches='tight')
        plt.close(fig)
        return self.filenames["forecast"]

    def plot_components(self, ticker, model, forecast):
        fig = model.plot_components(forecast)
        fig.suptitle(f"Forecast Components - {ticker}", fontsize=16)
        fig.savefig(os.path.join(self.image_path, self.filenames["components"]), bbox_inches='tight', dpi=300)
        plt.close(fig)
        return self.filenames["components"]

    def plot_hilo_strategy(self, price_data, best_period, ticker, hilo_long, hilo_short):
        if 'Date' not in price_data.columns:
            price_data['Date'] = price_data.index

        price_data['HiLo_Long'] = hilo_long
        price_data['HiLo_Short'] = hilo_short

        fig, ax = plt.subplots(figsize=(14, 7))

        ax.plot(price_data['Date'], price_data['Close'], label='Close Price', color='black')
        ax.plot(price_data['Date'], price_data['HiLo_Long'], label='HiLo Long', color='green', linestyle='--')
        ax.plot(price_data['Date'], price_data['HiLo_Short'], label='HiLo Short', color='red', linestyle='--')

        buy_signals = price_data['Close'] > price_data['HiLo_Long']
        sell_signals = price_data['Close'] < price_data['HiLo_Short']

        ax.plot(price_data.loc[buy_signals, 'Date'], price_data.loc[buy_signals, 'Close'], '^', markersize=10, color='g', label='Buy Signal')
        ax.plot(price_data.loc[sell_signals, 'Date'], price_data.loc[sell_signals, 'Close'], 'v', markersize=10, color='r', label='Sell Signal')

        ax.set_title(f"HiLo Activator Strategy for {ticker} - Best Period: {best_period} Days")
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
        fig.autofmt_xdate()

        fig.savefig(os.path.join(self.image_path, self.filenames["HiLo_Strategy"]))
        plt.close(fig)
        return self.filenames["HiLo_Strategy"]

    def plot_correlation(self, prices, title='Stock Correlation Matrix'):
        """
        Plota a matriz de correlação dos retornos dos ativos.

        :param prices: DataFrame com os preços de fechamento ajustados dos ativos.
        :param title: Título do gráfico.
        """
        correlation = prices.pct_change().corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, ax=ax, cmap='coolwarm', fmt=".2f")
        ax.set_title(title)

        fig.savefig(os.path.join(self.image_path, self.filenames["correlation_matrix"]))
        plt.close(fig)
        return self.filenames["correlation_matrix"]

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

        plt.savefig(os.path.join(self.image_path, self.filenames["candlestick_RSI"]))
        plt.close('all')
        return self.filenames["candlestick_RSI"]

    def plot_garch_volatility(self, futura_volatilidade):
        fig, ax = plt.subplots(figsize=(10, 6))
        futura_volatilidade.plot(ax=ax, title='Previsão de Volatilidade - Modelo GARCH')
        ax.set_xlabel('Dias Futuros')
        ax.set_ylabel('Volatilidade (%)')
        ax.legend(['Volatilidade Prevista'])

        fig.savefig(os.path.join(self.image_path, self.filenames["volatility"]))
        plt.close(fig)
        return self.filenames["volatility"]

    def plot_cross_validation_metric(self, df_cv, metric, title, ticker):
        fig = plt.figure(figsize=(10, 6))
        plot_cross_validation_metric(df_cv, metric=metric, ax=fig.add_subplot(111))
        plt.title(f"{title} - {ticker}")

        fig.savefig(os.path.join(self.image_path, self.filenames["metric"]), dpi=300)
        plt.close(fig)
        return self.filenames["metric"]
