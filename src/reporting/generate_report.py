import logging
import os

from reportlab.lib.units import inch
from src.analysis.indicator_calculator import IndicatorCalculator
from src.analysis.prophet_analysis import ProphetAnalysis
from src.analysis.strategy_evaluator import StrategyEvaluator
from src.analysis.volatility_analysis import VolatilityAnalysis
from src.plotting.plotter import Plotter
from src.reporting.pdf_report import PDFReportBuilder, PDFReporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, ticker, data, period='5y', last_days=60, future_periods=30, report_path=None):
        self.ticker = ticker
        self.data = data
        self.period = period
        self.last_days = last_days
        self.future_periods = future_periods
        self.filenames = []
        self.descriptions = {}
        self.titles = []
        self.plotter = Plotter()
        self.report_path = report_path
        self.builder = PDFReportBuilder(report_path, self.plotter.image_path)

    def append_image_if_exists(self, image_path):
        full_path = os.path.join(self.plotter.image_path, image_path)
        if os.path.isfile(full_path):
            self.filenames.append(full_path)
            return True
        logging.warning(f"Imagem não encontrada: {full_path}")
        return False

    def generate_report(self):
        logging.info("Iniciando a geração do relatório")
        self.generate_indicator_calculator()
        self.generate_prophet_analysis()
        self.generate_strategy_evaluator()
        self.generate_volatility_analysis()
        self.builder.build(self.ticker, self.titles, list(self.descriptions.values()), self.filenames)
        logging.info("Geração do relatório concluída")

    def generate_prophet_analysis(self):
        logging.info("Gerando análise do Prophet")
        prophet = ProphetAnalysis(self.ticker, self.data, self.future_periods)
        prophet.run_analysis()
        self.descriptions['Prophet'] = f"Modelo: {prophet.model}"
        self.titles.append('Análise de Séries Temporais com Prophet')
        self.append_image_if_exists(f"forecast_{self.ticker}.png")
        self.append_image_if_exists(f"mape_metric_{self.ticker}.png")
        self.append_image_if_exists(self.plotter.plot_last_days_forecast(self.data, prophet.forecast, self.future_periods, self.ticker))

    def generate_indicator_calculator(self):
        logging.info("Generating statistical analysis")
        self.data = IndicatorCalculator.calculate_RSI(self.data)
        self.data = IndicatorCalculator.calculate_EMA(self.data)
        self.data = IndicatorCalculator.calculate_HiLo(self.data)

        self.descriptions['Indicator Calculator'] = "Analysis with RSI, EMA, and HiLo indicators."
        self.titles.append('Análise Estatística')

        self.plotter.plot_with_indicators(self.data, last_days=self.last_days)

        chart_filename = f"candlestick_RSI_{self.last_days}_days.png"
        self.filenames.append(os.path.join(self.plotter.image_path, chart_filename))

        logging.info("Statistical analysis and chart generation completed.")

    def generate_strategy_evaluator(self):
        logging.info("Generating strategy evaluation")
        price_data = self.data[['High', 'Low', 'Close']].copy()
        bounds = [(1, 100)]
        best_period, best_score = StrategyEvaluator.optimize_strategy(price_data, bounds)
        hilo_long, hilo_short = StrategyEvaluator.hilo_activator(price_data['High'], price_data['Low'], int(best_period))
        self.plotter.plot_hilo_strategy(price_data, best_period, self.ticker, hilo_long, hilo_short)
        self.filenames.append(os.path.join(self.plotter.image_path, f"HiLo_Strategy_{self.ticker}.png"))
        description = f"Melhor período para HiLo Activator: {best_period} dias, Resultado da Estratégia: {best_score:.2f}"
        self.descriptions['Strategy Evaluation'] = description
        self.titles.append('Avaliação da Estratégia HiLo Activator')

    def generate_volatility_analysis(self):
        logging.info("Generating volatility analysis")
        volatility_analysis = VolatilityAnalysis(self.data['Retornos'])
        futura_volatilidade = volatility_analysis.analyze()
        self.plotter.plot_garch_volatility(futura_volatilidade, f"volatility_{self.ticker}.png")
        self.filenames.append(os.path.join(self.plotter.image_path, f"volatility_{self.ticker}.png"))

    def clean_up_files(self):
        logging.info("Cleaning up generated files")
        for file in self.filenames:
            filepath = os.path.join(os.getcwd(), file)
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"Deleted file: {file}")

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
