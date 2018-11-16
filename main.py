import time
from bot import Bot


MOON = Bot()
while True:
    MOON.tick()
    time.sleep(300)
