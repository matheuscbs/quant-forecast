import pandas as pd


class IndicatorCalculator:
    @staticmethod
    def calculate_RSI(data, column='y', period=14):
        """
        Calcula o Índice de Força Relativa (RSI) para os dados fornecidos.

        :param data: DataFrame do pandas contendo os dados de preços.
        :param column: A coluna do DataFrame de onde o RSI deve ser calculado.
        :param period: O número de períodos a serem usados no cálculo do RSI.
        :return: DataFrame do pandas com uma nova coluna 'RSI' adicionada.
        """
        delta = data[column].diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        avg_gains = gains.rolling(window=period, min_periods=1).mean()
        avg_losses = losses.rolling(window=period, min_periods=1).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        data['RSI'] = rsi
        return data

    @staticmethod
    def calculate_EMA(data, column='y', period=21):
        """
        Calcula a Média Móvel Exponencial (EMA) para os dados fornecidos.

        :param data: DataFrame do pandas contendo os dados de preços.
        :param column: A coluna do DataFrame de onde a EMA deve ser calculada.
        :param period: O número de períodos a serem usados no cálculo da EMA.
        :return: DataFrame do pandas com uma nova coluna 'EMA_{period}' adicionada.
        """
        ema = data[column].ewm(span=period, adjust=False).mean()
        data[f'EMA_{period}'] = ema
        return data

    @staticmethod
    def calculate_HiLo(data, high_column='High', low_column='Low', period=14):
        """
        Calcula os máximos (Hi) e mínimos (Lo) para um período específico.

        :param data: DataFrame do pandas contendo os dados de preços.
        :param high_column: A coluna do DataFrame para calcular o máximo.
        :param low_column: A coluna do DataFrame para calcular o mínimo.
        :param period: O número de períodos a serem usados no cálculo.
        :return: DataFrame do pandas com novas colunas 'HiLo_High' e 'HiLo_Low' adicionadas.
        """
        data['HiLo_High'] = data[high_column].rolling(window=period).max()
        data['HiLo_Low'] = data[low_column].rolling(window=period).min()
        return data
