import os

TICKER = 'BTC/USDT'
BASE_DIR = "/app"
REPORT_PATH = os.path.join(BASE_DIR, "relatorios/")
IMAGE_PATH = os.path.join(REPORT_PATH, "images/")
DEFAULT_PERIOD = '1m'
DEFAULT_LAST_DAYS = 30
DEFAULT_FUTURE_PERIODS = 15
INTRADAY_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '90m', '1d']
DEFAULT_INTERVAL = '1d'
N_TRIALS = 1
N_JOBS = 5
