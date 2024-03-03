from abc import ABC, abstractmethod


class IAnalysis(ABC):
    @abstractmethod
    def analyze(self):
        pass
