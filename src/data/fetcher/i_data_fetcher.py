from abc import ABC, abstractmethod


class IDataFetcher(ABC):
    @abstractmethod
    def fetch_data(self, ticker, period):
        pass
