import config
from src.data.fetcher.crypto_data_fetcher import CryptoDataFetcher
from src.data.fetcher.data_fetcher import YahooFinanceFetcher
from src.reporting.generate_report import ReportGenerator
from src.reporting.pdf_report import PDFReportBuilder


def is_crypto(ticker):
    return '/' in ticker

def process_ticker(ticker):

    if is_crypto(ticker):
        data_fetcher = CryptoDataFetcher()
    else:
        data_fetcher = YahooFinanceFetcher()

    data = data_fetcher.fetch_data(ticker=ticker)

    if data is not None and not data.empty:
        print(f"Dados para {ticker}: ", data.columns)
        report_generator = ReportGenerator(data, ticker=ticker)
        report_generator.generate_report()
        report_generator.clean_up_files()
    else:
        print(f"Não foi possível buscar os dados para {ticker}.")

if __name__ == "__main__":
    for ticker in config.tickers:
        if is_crypto(ticker):
            process_ticker(ticker)
        else:
            for ticker in config.set_next_ticker():
                process_ticker(ticker)
