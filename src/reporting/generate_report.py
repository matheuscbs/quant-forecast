import logging
import os

from src.analysis.prophet_analysis import ProphetAnalysis
from src.data import data_fetcher
from src.plotting.plotter import Plotter
from src.reporting.pdf_report import PDFReporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, ticker, period='5y', last_days=60, future_periods=30):
        self.ticker = ticker
        self.period = period
        self.last_days = last_days
        self.future_periods = future_periods
        self.plotter = Plotter()
        self.report_path = f"/app/relatorios/Relatorio_Analise_{self.ticker}.pdf"
        self.filenames = []
        self.titles = []
        self.descriptions = {}

    def generate_report(self):
        logging.info("Starting report generation")
        self.generate_statistical_analysis()
        self.generate_prophet_analysis()
        self.generate_plots()
        self.generate_pdf_report()
        logging.info("Report generation completed")

    def generate_prophet_analysis(self):
        logging.info("Generating Prophet analysis")
        prophet = ProphetAnalysis(self.ticker, self.period, self.future_periods)
        prophet.run_analysis()
        self.descriptions['Prophet'] = f"Modelo: {prophet.model}"
        self.titles.append('Análise de Séries Temporais com Prophet')
        self.filenames.append(f"forecast_{self.ticker}.png")
        self.filenames.append(f"mape_metric_{self.ticker}.png")

    """ TODO: Implement statistical analysis """
    def generate_statistical_analysis(self):
        pass

    """ TODO: Implement plotting """
    def generate_plots(self):
        pass

    def generate_pdf_report(self):
        logging.info("Generating PDF report")
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        reporter = PDFReporter(self.report_path)
        for title, description in zip(self.titles, self.descriptions.values()):
            reporter.add_paragraph(f"{title}\n{description}")
        for filename in self.filenames:
            if os.path.exists(filename):
                reporter.add_image(filename)
            else:
                logging.warning(f"File {filename} does not exist. Skipping.")
        reporter.build_pdf()
        logging.info(f"PDF report generated at {self.report_path}")
        os.system(f"open {self.report_path}")

    def __del__(self):
        logging.info("Cleaning up generated files")
        for file in self.filenames:
            if os.path.exists(file):
                os.remove(file)
                logging.info(f"Deleted file: {file}")

if __name__ == "__main__":
    ticker = 'PETR4.SA'
    data_fetch = data_fetcher.DataFetcher()
    data = data_fetch.fetch_data(ticker, period='5y')
    report_generator = ReportGenerator(ticker, data)
    report_generator.generate_report()
