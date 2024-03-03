from src.data.data_fetcher import YahooFinanceFetcher
from src.reporting.generate_report import ReportGenerator
from src.reporting.pdf_report import PDFReportBuilder

if __name__ == "__main__":
    ticker = 'PETR4.SA'
    period = '5y'

    data_fetcher = YahooFinanceFetcher()
    data = data_fetcher.fetch_data(ticker, period)

    if data is not None:
        builder = PDFReportBuilder(f"/app/relatorios/Relatorio_Analise_{ticker}.pdf")

        report_generator = ReportGenerator(builder, ticker, data, period)
        report_generator.generate_report()
    else:
        print(f"Não foi possível buscar os dados para {ticker}.")
