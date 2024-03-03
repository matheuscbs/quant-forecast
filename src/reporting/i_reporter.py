from abc import ABC, abstractmethod


class ReportBuilder(ABC):
    @abstractmethod
    def add_title(self, title):
        pass

    @abstractmethod
    def add_paragraph(self, text):
        pass

    @abstractmethod
    def add_image(self, image_path):
        pass

    @abstractmethod
    def build(self):
        pass
