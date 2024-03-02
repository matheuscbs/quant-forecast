import logging
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import yfinance as yf


class IDataFetcher(ABC):
    @abstractmethod
    def fetch_data(self, ticker, period):
        pass

class YahooFinanceFetcher(IDataFetcher):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def fetch_data(self, ticker, period):
        self.logger.info(f"Iniciando o download de dados para {ticker} com Yahoo Finance...")
        try:
            data = yf.download(ticker, period=period)
            if data.empty:
                self.logger.warning(f"Nenhum dado encontrado para {ticker} no período especificado.")
                return None
            data = self._prepare_data(data)
            self.logger.info(f"Dados para {ticker} baixados com sucesso.")
            return data
        except Exception as e:
            self.logger.error(f"Erro ao baixar os dados para {ticker}: {e}")
            return None

    def _prepare_data(self, data):
        data.reset_index(inplace=True)
        data.rename(columns={"Date": "ds", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Adj Close": "y", "Volume": "Volume"}, inplace=True)
        data['ds'] = pd.to_datetime(data['ds'])
        data.dropna(how='all', inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        if data.isnull().values.any():
            data.fillna(method='ffill', inplace=True)
        data['Retornos'] = np.log(data['y'] / data['y'].shift(1))
        return data
