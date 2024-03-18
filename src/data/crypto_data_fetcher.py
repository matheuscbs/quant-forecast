import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import ccxt
import config
import pandas as pd
from src.data.i_data_fetcher import IDataFetcher


class CryptoDataFetcher(IDataFetcher):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchange = ccxt.binance()
        self.max_request_limit = 1000

    def _calculate_since_from_period(self, period):
        period_value = int(period[:-1])
        period_unit = period[-1]

        if period_unit == 'y':
            since_date = datetime.now() - timedelta(days=365 * period_value)
        elif period_unit == 'm':
            since_date = datetime.now() - timedelta(days=30 * period_value)
        elif period_unit == 'd':
            since_date = datetime.now() - timedelta(days=period_value)
        else:
            self.logger.error("Unidade de período não reconhecida. Usando padrão de 1 ano.")
            since_date = datetime.now() - timedelta(days=365)

        return int(since_date.timestamp() * 1000)

    def _interval_to_milliseconds(self, interval):
        unit = interval[-1]
        if unit == 'm':
            return int(interval[:-1]) * 60 * 1000
        elif unit == 'h':
            return int(interval[:-1]) * 3600 * 1000
        elif unit == 'd':
            return int(interval[:-1]) * 24 * 3600 * 1000
        else:
            self.logger.error("Intervalo não suportado. Usando '1h' como padrão.")
            return 3600 * 1000

    def _fetch_ohlcv(self, ticker, since, limit):
        try:
            ohlcv = self.exchange.fetch_ohlcv(ticker, config.DEFAULT_INTERVAL, since=since, limit=limit)
            time.sleep(self.exchange.rateLimit / 1000)
            return ohlcv
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados OHLCV: {e}")
            return []

    def fetch_data(self):
        since_timestamp = self._calculate_since_from_period(config.DEFAULT_PERIOD)
        interval_ms = self._interval_to_milliseconds(config.DEFAULT_INTERVAL)
        end_timestamp = self.exchange.milliseconds()

        hours_diff = int((end_timestamp - since_timestamp) / interval_ms)
        segments = [(config.TICKER, since_timestamp + i * interval_ms, self.max_request_limit) for i in range(min(hours_diff, self.max_request_limit))]

        all_data = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self._fetch_ohlcv, segment[0], segment[1], segment[2]) for segment in segments]
            for future in as_completed(futures):
                ohlcv = future.result()
                if ohlcv:
                    all_data.extend(ohlcv)

        all_data.sort(key=lambda x: x[0])

        dados = pd.DataFrame(all_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        dados['Timestamp'] = pd.to_datetime(dados['Timestamp'], unit='ms')
        dados.rename(columns={"Timestamp": "ds", "Close": "y"}, inplace=True)
        dados['Close'] = dados['y']
        dados['ds'] = dados['ds'].dt.tz_localize(None)
        dados.fillna(method='ffill', inplace=True)
        dados['Retornos'] = dados['y'].pct_change()
        return dados
