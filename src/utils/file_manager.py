import os


class FileManager:
    @staticmethod
    def normalize_ticker_name(ticker):
        """Normaliza o nome do ticker substituindo caracteres especiais."""
        return ticker.replace("/", "_")

    @staticmethod
    def ensure_directory_exists(directory_path):
        """Assegura que o diretório exista."""
        os.makedirs(directory_path, exist_ok=True)
