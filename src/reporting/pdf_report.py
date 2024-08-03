import logging
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFReporter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.document = SimpleDocTemplate(filepath, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.elements = []

    def _add_paragraph(self, text, style):
        try:
            if isinstance(text, list):
                text = " ".join(text)
            self.elements.append(Paragraph(str(text), self.styles[style]))
            self.elements.append(Spacer(1, 12))
        except Exception as e:
            logging.error(f"Erro ao adicionar parágrafo: {e}")

    def _add_image(self, image_path):
        if os.path.isfile(image_path):
            self.elements.append(Image(image_path, width=6 * inch, height=4 * inch))
            self.elements.append(Spacer(1, 12))
        else:
            logging.warning(f"Imagem não encontrada: {image_path}")

    def generate_report(self, ticker, titles, descriptions, filenames_list):
        self._add_paragraph(f"Relatório de Análise - {ticker}", 'Title')

        for title, description, filenames in zip(titles, descriptions, filenames_list):
            self._add_paragraph(title, 'Heading2')
            self._add_paragraph(description, 'Normal')
            for image_path in filenames:
                self._add_image(image_path)

        self.document.build(self.elements)

class PDFReportBuilder:
    def __init__(self, filepath):
        self.reporter = PDFReporter(filepath)

    def build(self, ticker, titles, descriptions, filenames_list):
        self.reporter.generate_report(ticker, titles, descriptions, filenames_list)
