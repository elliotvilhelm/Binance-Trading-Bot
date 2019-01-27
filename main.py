import time
from bot import Bot


MOON = Bot(base_coin='BTC', symbols=['XRP'], backtest=False)
# MOON.run_backtest()
while True:
    MOON.tick()
    time.sleep(1)
