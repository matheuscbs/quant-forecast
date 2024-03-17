import logging
from datetime import datetime, timedelta

import config
import numpy as np
import pandas as pd
import yfinance as yf
from src.data.i_data_fetcher import IDataFetcher


class YahooFinanceFetcher(IDataFetcher):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def fetch_data(self, ticker=config.TICKER, period=config.DEFAULT_PERIOD, interval=config.DEFAULT_INTERVAL):
        period_in_days = self._calculate_period_in_days(period)

        if interval == '1d' or period_in_days <= 730:
            return self._fetch_single_period_data(ticker, period_in_days, interval)
        else:
            return self._fetch_intraday_data_concatenated(ticker, period_in_days, interval)

    def _calculate_period_in_days(self, period):
        try:
            period_value = int(period[:-1])
            period_unit = period[-1]
            if period_unit == 'y':
                return period_value * 365
            else:
                self.logger.error(f"Unidade de período '{period_unit}' não reconhecida.")
                return 0
        except ValueError:
            self.logger.error("Erro ao converter período para dias.")
            return 0

    def _fetch_single_period_data(self, ticker, period, interval):
        self.logger.info(f"Iniciando o download de dados para {ticker} com intervalo de {interval} via Yahoo Finance...")
        try:
            period_str = f"{period}d" if isinstance(period, int) else str(period)
            data = yf.download(ticker, period=period_str, interval=interval)
            if data.empty:
                self.logger.warning(f"Nenhum dado encontrado para {ticker} no período especificado.")
                return None
            data = self._prepare_data(data)
            self.logger.info(f"Dados para {ticker} baixados com sucesso.")
            return data
        except Exception as e:
            self.logger.error(f"Erro ao baixar os dados para {ticker}: {e}")
            return None

    def _fetch_intraday_data_concatenated(self, ticker, period_in_days, interval):
        self.logger.info(f"Iniciando o download de dados intradiários para {ticker} com intervalo de {interval} e período de {period_in_days} dias...")

        end_date = datetime.now()
        start_date = max(end_date - timedelta(days=period_in_days), datetime.now() - timedelta(days=730))
        all_data = []

        while period_in_days > 0:
            try:
                self.logger.info(f"Baixando dados de {start_date.date()} até {end_date.date()}")
                temp_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval=interval)
                if not temp_data.empty:
                    all_data.append(temp_data)
                    period_in_days -= (end_date - start_date).days
                    end_date = start_date - timedelta(days=1)
                    start_date = max(end_date - timedelta(days=730), end_date - timedelta(days=period_in_days))
                else:
                    self.logger.warning("Dados vazios recebidos; interrompendo busca.")
                    break
            except Exception as e:
                self.logger.error(f"Erro ao baixar os dados para {ticker} entre {start_date} e {end_date}: {e}")
                break

        if all_data:
            all_data = pd.concat(all_data)
            return self._prepare_data(all_data)
        else:
            self.logger.warning(f"Nenhum dado intradiário encontrado para {ticker}.")
            return None

    def _prepare_data(self, data):
        data.reset_index(inplace=True)
        data.columns = ['ds' if str(col).lower() in ['date', 'datetime'] else col for col in data.columns]
        data['ds'] = pd.to_datetime(data['ds'], errors='coerce', utc=True).dt.tz_localize(None)
        if data['ds'].isnull().any():
            self.logger.warning("Algumas datas não puderam ser convertidas e serão removidas.")
            data = data.dropna(subset=['ds'])
        data.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Adj Close": "y", "Volume": "Volume"}, inplace=True)
        data.dropna(how='all', inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        if data.isnull().values.any():
            data.fillna(method='ffill', inplace=True)
        data['Retornos'] = np.log(data['y'] / data['y'].shift(1))
        return data
