import json
import sys
import time

import machine
import gc

from simple import MQTTClient


# D1 mini pin 	ESP8266 pin 	MicroPython eg.
# TX 	GPIO1 	machine.Pin(1)
# RX 	GPIO3 	machine.Pin(3)
# D0 	GPIO16 	machine.Pin(16)
# D1 	GPIO5 	machine.Pin(5)
# D2 	GPIO4 	machine.Pin(4)
# D3 	GPIO0 	machine.Pin(0)
# D4 	GPIO2 	machine.Pin(2)
# D5 	GPIO14 	machine.Pin(14)
# D6 	GPIO12 	machine.Pin(12)
# D7 	GPIO13 	machine.Pin(13)
# D8 	GPIO15 	machine.Pin(15)


class WsWemos:
    PIN_LED = 2
    PIN_RELAY = 14
    toggle = 1  # 1 = AUS
    server = None

    def __init__(self, server="192.168.178.35"):
        print('WsWemos __init__()')
        self.server = server
        self.devicename = "wemosmicropython"
        self.TOPIC = b"/to/#"
        self.connect()
        payload = {}
        payload["device"] = self.devicename
        payload["time"] = time.localtime()
        self.c.publish(b"/from_device/signon", json.dumps(payload))

        self.pinLED = machine.Pin(self.PIN_LED, machine.Pin.OUT)  # an
        self.pinLED.value(self.toggle)

        self.switch = machine.Pin(self.PIN_RELAY, machine.Pin.IN)  # aus

    def connect(self):
        while True:
            try:
                self.c = MQTTClient("umqtt_client", self.server)
                self.c.set_callback(self.sub)
                self.c.connect()
                self.c.subscribe(self.TOPIC)  # alle to meldungen
                print("WsWemos connect - Connected to %s, subscribed to %s topic" % (self.server, self.TOPIC))
                return
            except OSError as e:
                print("WsWemos connect - MQTT can't connect", e)
                time.sleep(1)

    def ping(self):
        self.c.ping()

    # Received messages from subscriptions will be delivered to this callback
    def sub(self, topic, msg):
        print(topic, msg)
        payload = json.loads(msg)
        print(payload)
        if topic == b'/to/switch':
            switchvalue = payload['value']
            print("Schalter: ", switchvalue)
            if switchvalue == 'on':
                self.switch = machine.Pin(self.PIN_RELAY, machine.Pin.OUT)
                self.switch.value(0)
            else:
                self.switch = machine.Pin(self.PIN_RELAY, machine.Pin.IN)
            payload['switch'] = switchvalue
            self.send_status(payload)
        elif topic == b'/to/command':
            command = payload['value']
            print('command: ', command)
            sys.exit()
        elif topic == b'/to/LED':
            if self.toggle == 0:
                self.toggle = 1
            else:
                self.toggle = 0
            self.pinLED.value(self.toggle)
        elif topic == b'/to/status':
            self.c.publish(b"/from_device/status", json.dumps(payload))

    def send_status(self, payload):
        payload['free_mem'] = gc.mem_free()
        self.c.publish(b"/from_device/status", json.dumps(payload))

    def checkMessage(self):
        self.c.check_msg()
