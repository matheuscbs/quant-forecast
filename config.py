import os

# tickers = ['SUZB3', 'KLBN3', 'CRFB3', 'BPAC3', 'GFSA3', 'SAPR4', 'BMEB4', 'CMIG4', 'AURE3', 'EUCA4', 'MGLU3', 'AGRO3', 'ROMI3', 'JHSF3', 'FESA4', 'COCE5', 'JBSS3', 'BMGB4', 'BHIA3', 'VIVT3', 'TASA4', 'PCAR3', 'ASAI3', 'TAEE11', 'LREN3', 'MRVE3', 'ITUB4', 'ITSA4', 'WEGE3', 'PETR4', 'VALE3', 'BBAS3', 'BRAP4', 'CMIN3', 'CSNA3', 'USIM5']
# tickers = ['CMIG4', 'BBAS3', 'USIM5', 'BRAP4']
tickers = ['BTC/USDT']
CURRENT_TICKER = None
BASE_DIR = "/app"
REPORT_PATH = os.path.join(BASE_DIR, "relatorios/")
IMAGE_PATH = os.path.join(REPORT_PATH, "images/")
DEFAULT_PERIOD = '1w'
DEFAULT_LAST_DAYS = 30
DEFAULT_FUTURE_PERIODS = 15
INTRADAY_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '90m', '1d']
DEFAULT_INTERVAL = '1h'
N_TRIALS = 1
N_JOBS = 10
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/investimentos_db')

def set_next_ticker():
    global CURRENT_TICKER
    for ticker in tickers:
        CURRENT_TICKER = ticker + ".SA"
        yield CURRENT_TICKER
