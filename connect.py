import time

import network
import ubinascii


class Connect:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        print('Connect __init__()')

    def isConnected(self):
        return self.wlan.isconnected()

    def getMac(self):
        return ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()

    def do_connect(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connect do_connect() - connecting to network...')
            self.wlan.connect('claube', 'Nismipf01!')
            while not self.wlan.isconnected():
                print(".")
                time.sleep(1)

        print('Connect do_connect() - network config:', self.wlan.ifconfig())
