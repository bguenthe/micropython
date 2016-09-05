import time

import machine
import gc
import webrepl

from connect import Connect
from ws_wemos import WsWemos


# mosquitto_pub -t '/to/switch' -m '{"value": "on"}'
# mosquitto_pub -t '/to/switch' -m '{"value": "off"}'
# mosquitto_pub -t '/to/command' -m '{"value": "exit"}'
# mosquitto_pub -t '/to/status' -m '{"lala": "ldld"}'

class Main:
    def __init__(self):
        webrepl.start()

    def main(self):
        i = 0
        c = Connect()
        c.do_connect()
        w = WsWemos()
        t = time.time()
        while True:
            if c.isConnected() == False:
                c.do_connect()
                w.connect()

            try:
                w.checkMessage()
                # if i % 10 == 0: # alle 10 sec
                #     w.ping()
            except OSError as e:
                print("Main main - WsWemos checkMessage failed", e)
                w.connect()

                # i += 1
                # print("durchläufe: ", i)
                # time.sleep(1)


if __name__ == "__main__":
    try:
        m = Main()
        m.main()
    except:
        print("Main - __main__: reset")
        machine.reset()
