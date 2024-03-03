from scipy.optimize import differential_evolution


class StrategyEvaluator:
    @staticmethod
    def hilo_activator(highs, lows, period):
        hilo_long = highs.rolling(window=period).max()
        hilo_short = lows.rolling(window=period).min()
        return hilo_long, hilo_short

    @staticmethod
    def evaluate_strategy(parameters, price_data):
        period = int(parameters[0])
        hilo_long, hilo_short = StrategyEvaluator.hilo_activator(price_data['High'], price_data['Low'], period)

        price_data['Signal'] = 0
        price_data.loc[price_data['Close'] > hilo_long.shift(1), 'Signal'] = 1
        price_data.loc[price_data['Close'] < hilo_short.shift(1), 'Signal'] = -1

        price_data['Strategy_Returns'] = price_data['Signal'].shift(1) * price_data['Close'].pct_change()
        return -price_data['Strategy_Returns'].cumsum().iloc[-1]

    @staticmethod
    def optimize_strategy(price_data, bounds):
        result = differential_evolution(StrategyEvaluator.evaluate_strategy, bounds, args=(price_data,))
        return result.x, -result.fun
