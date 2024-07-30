import logging
import signal
import warnings

import config
from dask.distributed import Client
from src.data.fetcher.crypto_data_fetcher import CryptoDataFetcher
from src.data.fetcher.data_fetcher import YahooFinanceFetcher
from src.reporting.generate_report import ReportGenerator
from src.reporting.pdf_report import PDFReportBuilder


def signal_handler(signal, frame):
    logging.warning("KeyboardInterrupt detected, shutting down Dask client gracefully...")
    client.shutdown()
    exit(1)

warnings.filterwarnings("ignore", category=FutureWarning, module="prophet.plot")

def is_crypto(ticker):
    return "/" in ticker

def process_ticker(ticker, client):
    if is_crypto(ticker):
        data_fetcher = CryptoDataFetcher()
    else:
        data_fetcher = YahooFinanceFetcher()

    data = data_fetcher.fetch_data(ticker=ticker)

    if data is not None and not data.empty:
        print(f"Dados para {ticker}: ", data.columns)
        report_generator = ReportGenerator(data, ticker=ticker, client=client)
        report_generator.generate_report()
        report_generator.clean_up_files()
    else:
        print(f"Não foi possível buscar os dados para {ticker}.")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    with Client() as client:
        for ticker in config.tickers:
            if is_crypto(ticker):
                process_ticker(ticker, client)
            else:
                for ticker in config.set_next_ticker():
                    process_ticker(ticker, client)
