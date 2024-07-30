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
        period_in_days = self._calculate_period_in_days(period)

        self.logger.info(f"Iniciando a busca de dados para {ticker} com período de {period} ({period_in_days} dias) e intervalo de {interval}.")

        if interval == '1d' or period_in_days <= 730:
            data = self._fetch_single_period_data(ticker, period_in_days, interval)
        else:
            data = self._fetch_intraday_data_concatenated(ticker, period_in_days, interval)

        if data is not None:
            self.logger.info(f"Busca de dados para {ticker} concluída com sucesso. Total de registros: {len(data)}")
        else:
            self.logger.warning(f"Não foram encontrados dados para {ticker} com os parâmetros fornecidos.")

        return data

    def _calculate_period_in_days(self, period):
        """
        Calcula o período em dias com base na string de período.
        """
        try:
            period_value = int(period[:-1])
            period_unit = period[-1]
            if period_unit == 'y':
                return period_value * 365
            else:
                self.logger.error(f"Unidade de período '{period_unit}' não reconhecida.")
                return 0
        except ValueError:
            self.logger.error(f"Erro ao converter período '{period}' para dias. Verifique o formato (ex: '1y', '6mo').")
            return 0

    def _fetch_single_period_data(self, ticker, period, interval):
        """
        Baixa dados para um único período contínuo.
        """
        self.logger.info(f"Baixando dados de período único para {ticker}...")
        try:
            period_str = f"{period}d" if isinstance(period, int) else str(period)
            data = yf.download(ticker, period=period_str, interval=interval)
            if data.empty:
                self.logger.warning(f"Nenhum dado encontrado para {ticker} no período especificado.")
                return None
            return self._prepare_data(data)
        except Exception as e:
            self.logger.error(f"Erro ao baixar os dados para {ticker}: {e}")
            return None

    def _fetch_intraday_data_concatenated(self, ticker, period_in_days, interval):
        """
        Baixa dados intradiários em partes (chunks) e os concatena.
        """

        self.logger.info(f"Baixando dados intradiários para {ticker} em lotes...")
        end_date = datetime.now()
        all_data = []

        max_days_per_request = 729 if interval == "1h" else 729

        while period_in_days > 0:
            days_to_request = min(period_in_days, max_days_per_request)
            start_date = end_date - timedelta(days=days_to_request)

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

            period_in_days -= days_to_request
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
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)

        if data.isnull().values.any():
            self.logger.warning("Dados nulos ainda presentes após o preenchimento. Substituindo por zero.")
            data.fillna(0, inplace=True)

        data['Retornos'] = np.log(data['y'] / data['y'].shift(1))

        self.logger.info(f"Preparo dos dados concluído. Total de registros: {len(data)}")
        return data
