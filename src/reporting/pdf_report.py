from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer


class PDFReporter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.document = SimpleDocTemplate(filepath, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.elements = []

    def add_paragraph(self, text, style='BodyText'):
        paragraph = Paragraph(text, self.styles[style])
        self.elements.append(paragraph)
        self.elements.append(Spacer(1, 12))

    def add_image(self, image_path, width=1 * inch, height=1 * inch):
        self.elements.append(Image(image_path, width=width, height=height))
        self.elements.append(Spacer(1, 12))

    def build_pdf(self):
        self.document.build(self.elements)
