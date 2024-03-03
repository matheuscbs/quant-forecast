import logging
import os

from src.analysis.indicator_calculator import IndicatorCalculator
from src.analysis.prophet_analysis import ProphetAnalysis
from src.analysis.strategy_evaluator import StrategyEvaluator
from src.analysis.volatility_analysis import VolatilityAnalysis
from src.plotting.plotter import Plotter
from src.reporting.pdf_report import PDFReporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, builder, ticker, data, period='5y', last_days=60, future_periods=30):
        self.builder = builder
        self.ticker = ticker
        self.data = data
        self.period = period
        self.last_days = last_days
        self.future_periods = future_periods
        self.filenames = []
        self.descriptions = {}
        self.titles = []
        self.plotter = Plotter()

    def generate_report(self):
        logging.info("Starting report generation")
        self.builder.add_title(f"Relatório de Análise - {self.ticker}")
        self.generate_indicator_calculator()
        self.generate_prophet_analysis()
        self.generate_strategy_evaluator()
        self.generate_volatility_analysis()
        self.generate_plots()
        self.builder.build()
        logging.info("Report generation completed")

    def generate_prophet_analysis(self):
        logging.info("Generating Prophet analysis")
        prophet = ProphetAnalysis(self.ticker, self.data, self.future_periods)
        prophet.run_analysis()
        self.descriptions['Prophet'] = f"Modelo: {prophet.model}"
        self.titles.append('Análise de Séries Temporais com Prophet')
        self.filenames.append(f"forecast_{self.ticker}.png")
        self.filenames.append(f"mape_metric_{self.ticker}.png")
        self.plotter.plot_last_days_forecast(self.data, prophet.forecast, self.future_periods, self.ticker)
        self.filenames.append(f"last_days_forecast_{self.ticker}.png")

    def generate_indicator_calculator(self):
        logging.info("Generating statistical analysis")
        self.data = IndicatorCalculator.calculate_RSI(self.data)
        self.data = IndicatorCalculator.calculate_EMA(self.data)
        self.filenames.append('RSI_plot.png')
        self.filenames.append('EMA_plot.png')

    def generate_strategy_evaluator(self):
        logging.info("Generating strategy evaluation")
        price_data = self.data[['High', 'Low', 'Close']].copy()
        bounds = [(1, 100)]
        best_period, best_score = StrategyEvaluator.optimize_strategy(price_data, bounds)
        self.plotter.plot_hilo_strategy(price_data, best_period, self.ticker)
        self.filenames.append(f"HiLo_Strategy_{self.ticker}.png")
        description = f"Melhor período para HiLo Activator: {best_period} dias, Resultado da Estratégia: {best_score:.2f}"
        self.descriptions['Strategy Evaluation'] = description
        self.titles.append('Avaliação da Estratégia HiLo Activator')

    def generate_volatility_analysis(self):
        logging.info("Generating volatility analysis")
        volatility_analysis = VolatilityAnalysis(self.data['Retornos'])
        futura_volatilidade = volatility_analysis.analyze()
        self.plotter.plot_garch_volatility(futura_volatilidade, f"volatility_{self.ticker}.png")
        self.filenames.append(f"volatility_{self.ticker}.png")

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
        try:
            if logging and hasattr(self, 'filenames'):
                logging.info("Cleaning up generated files")
                for file in self.filenames:
                    if os.path.exists(file):
                        os.remove(file)
                        if logging:
                            logging.info(f"Deleted file: {file}")
        except AttributeError:
            pass
