import esp
import machine
import webrepl

from connect import Connect
from ws_wemos import WsWemos


class Main:
    def __init__(self):
        webrepl.start()
        self.c = Connect()
        self.devicename = None
        try:
            f = open('devicename.config', 'r')
            self.devicename = f.read()
            f.close()
        except Exception as e:
            print("Main __init__ - Error %s", e)

    def main(self):
        self.c.do_connect()
        w = WsWemos(devicename=self.devicename, mac=self.c.getMac())
        esp.osdebug(None)

        while True:
            if self.c.isConnected() == False:
                self.c.do_connect()
                w.connect()

            try:
                w.checkMessage()
            except OSError as e:
                print("Main main - WsWemos checkMessage failed", e)
                w.connect()


if __name__ == "__main__":
    try:
        m = Main()
        m.main()
    except Exception as e:
        print("Main - __main__: reset. Error: %s", e)
        machine.reset()
