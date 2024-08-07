import logging
from datetime import datetime, timedelta

import config
import numpy as np
import pandas as pd
import yfinance as yf
from src.data.fetcher.i_data_fetcher import IDataFetcher


class YahooFinanceFetcher(IDataFetcher):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def fetch_data(self, ticker, period=config.DEFAULT_PERIOD, interval=config.DEFAULT_INTERVAL):
        """
        Baixa dados do Yahoo Finance, otimizando o download para dados intradiários.
        """
        self.logger.info(f"Iniciando a busca de dados para {ticker} com período de {period} e intervalo de {interval}.")

        if interval == '1d' or period not in ['max']:
            data = self._fetch_single_period_data(ticker, period, interval)
        else:
            data = self._fetch_intraday_data_concatenated(ticker, interval)

        if data is not None:
            self.logger.info(f"Busca de dados para {ticker} concluída com sucesso. Total de registros: {len(data)}")
        else:
            self.logger.warning(f"Não foram encontrados dados para {ticker} com os parâmetros fornecidos.")

        return data

    def _calculate_period_in_days(self, period):
        """ Calcula o período em dias com base na string de período. """
        try:
            period_value = int(period[:-1])
            period_unit = period[-1]
            if period_unit == 'y':
                return period_value * 365
            elif period_unit == 'mo':
                return period_value * 30
            elif period_unit == 'd':
                return period_value
            else:
                self.logger.error(f"Unidade de período '{period_unit}' não reconhecida.")
                return None
        except ValueError:
            self.logger.error(f"Erro ao converter período '{period}' para dias. Verifique o formato (ex: '1y', '6mo', '30d').")
            return None

    def _fetch_single_period_data(self, ticker, period, interval):
        """
        Baixa dados para um único período contínuo.
        """
        self.logger.info(f"Baixando dados de período único para {ticker}...")
        try:
            data = yf.download(ticker, period=period, interval=interval)
            if data.empty:
                self.logger.warning(f"Nenhum dado encontrado para {ticker} no período especificado.")
                return None
            return self._prepare_data(data)
        except Exception as e:
            self.logger.error(f"Erro ao baixar os dados para {ticker}: {e}")
            return None

    def _fetch_intraday_data_concatenated(self, ticker, interval):
        """
        Baixa dados intradiários em partes (chunks) e os concatena, respeitando a data de IPO da ação e o limite de dias por requisição para o intervalo especificado.
        """
        self.logger.info(f"Baixando dados intradiários para {ticker} em lotes...")

        end_date = datetime.now()

        # Obtém informações da ação, incluindo a data do IPO
        ticker_info = yf.Ticker(ticker)
        start_date_limit = ticker_info.info.get('firstTradeDate', datetime(2013, 1, 1))
        start_date_limit = start_date_limit.replace(tzinfo=None)

        all_data = []
        max_days_per_request = config.MAX_DAYS_PER_REQUEST.get(interval, 730)  # Obtém o limite de dias por requisição para o intervalo

        while end_date > start_date_limit:
            start_date = end_date - timedelta(days=max_days_per_request)

            self.logger.info(f"Baixando dados de {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}...")
            try:
                temp_data = yf.download(
                    ticker,
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    interval=interval,
                )

                if not temp_data.empty:
                    self.logger.info(f"Dados baixados com sucesso ({len(temp_data)} registros).")
                    all_data.append(temp_data)
                else:
                    self.logger.warning(f"Nenhum dado encontrado para {ticker} entre {start_date.strftime('%Y-%m-%d')} e {end_date.strftime('%Y-%m-%d')}")
            except Exception as e:
                self.logger.error(f"Erro ao baixar os dados para {ticker} entre {start_date.strftime('%Y-%m-%d')} e {end_date.strftime('%Y-%m-%d')}: {e}")

            end_date = start_date - timedelta(days=1)

        if all_data:
            self.logger.info("Concatenando os dados baixados...")
            all_data = pd.concat(all_data)
            return self._prepare_data(all_data)
        else:
            self.logger.warning(f"Nenhum dado intradiário encontrado para {ticker}.")
            return None

    def _prepare_data(self, data):
        """
        Prepara os dados para uso.
        """
        self.logger.info("Preparando os dados...")

        data.reset_index(inplace=True)
        data.columns = ['ds' if str(col).lower() in ['date', 'datetime'] else col for col in data.columns]
        data['ds'] = pd.to_datetime(data['ds'], errors='coerce', utc=True).dt.tz_localize(None)

        # Verifica e remove dados com datas inválidas
        invalid_dates = data['ds'].isnull()
        if invalid_dates.any():
            self.logger.warning(f"Removendo {invalid_dates.sum()} linhas com datas inválidas.")
            data = data[~invalid_dates]

        data.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Adj Close": "y", "Volume": "Volume"}, inplace=True)

        # Remove dados completamente nulos
        data.dropna(how='all', inplace=True)

        # Preenchimento de dados nulos
        data.ffill(inplace=True)
        data.bfill(inplace=True)

        if data.isnull().values.any():
            columns_with_nulls = data.columns[data.isnull().any()].tolist()
            self.logger.warning(f"Dados nulos ainda presentes após o preenchimento nas colunas: {columns_with_nulls}. Substituindo por zero.")
            data.fillna(0, inplace=True)

        data['Retornos'] = np.log(data['y'] / data['y'].shift(1))
        data['Retornos'] = data['Retornos'].fillna(0)

        self.logger.info(f"Preparo dos dados concluído. Total de registros: {len(data)}")
        return data
