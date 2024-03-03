import logging
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFReporter:
    def __init__(self, filepath, image_path):
        self.filepath = filepath
        self.image_path = image_path  # Adiciona o caminho da imagem como um atributo de instância
        self.document = SimpleDocTemplate(filepath, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.elements = []

    def generate_report(self, ticker, titles, descriptions, filenames):
        self.elements.append(Paragraph(f"Relatório de Análise - {ticker}", self.styles['Title']))
        self.elements.append(Spacer(1, 12))

        for title, description, filename in zip(titles, descriptions, filenames):
            self.elements.append(Paragraph(title, self.styles['Heading2']))
            self.elements.append(Spacer(1, 12))
            self.elements.append(Paragraph(description, self.styles['Normal']))
            self.elements.append(Spacer(1, 12))

            image_path = os.path.join(self.image_path, filename)
            if os.path.exists(image_path):
                self.elements.append(Image(image_path, width=6 * inch, height=4 * inch))
                self.elements.append(Spacer(1, 12))
            else:
                logging.warning(f"Image not found: {image_path}")

        self.document.build(self.elements)

class PDFReportBuilder:
    def __init__(self, filepath, image_path):
        self.reporter = PDFReporter(filepath, image_path)

    def build(self, ticker, titles, descriptions, filenames):
        self.reporter.generate_report(ticker, titles, descriptions, filenames)
