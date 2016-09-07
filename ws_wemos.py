import gc
import json
import sys
import time

import machine

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

# mosquitto_pub -t '5c:cf:7f:83:0d:69/to_device/switch' -m '{"value": "off"}'
# mosquitto_pub -t '5c:cf:7f:83:0d:69/to_device/LED' -m '{"value": "off"}'
# mosquitto_pub -t '5c:cf:7f:83:0d:69/to_device/command' -m '{"value": "setdevicename", "name": "wemos2"}'


class WsWemos:
    PIN_LED = 2
    PIN_RELAY = 14
    server = None
    switchstatus = 0
    ledstatus = 0

    def __init__(self, server="192.168.178.35", devicename=None, mac=None):
        print('WsWemos __init__() devivename: %s mac: %s', devicename, mac)
        self.server = server
        if devicename is None:
            devicename = mac
        self.devicename = devicename.encode()
        self.TOPIC = self.devicename + b"/to_device/#"  # alle für dieses Gerät
        self.mac = mac

        self.connect()
        payload = {}
        payload["device"] = self.devicename
        payload["time"] = time.localtime()
        self.c.publish(self.devicename + b"/from_device/signon", json.dumps(payload))

        self.pinLED = machine.Pin(self.PIN_LED, machine.Pin.OUT)  # an
        self.pinLED.value(1)  # aus
        self.ledstatus = 0

        self.switch = machine.Pin(self.PIN_RELAY, machine.Pin.IN)  # aus
        self.switchstatus = 0

    def connect(self):
        print('WsWemos connect')
        while True:
            try:
                self.c = MQTTClient(self.devicename, self.server)
                self.c.set_callback(self.sub)
                self.c.connect()
                self.c.subscribe(self.TOPIC)  # alle to Meldungen an dieses Gerät
                self.c.subscribe(b'to_device/#')  # broadcast
                print("WsWemos connect - Connected to %s, subscribed to %s %s topic" % (
                    self.server, self.TOPIC, 'to_device'))
                self.startticks = time.ticks_ms()
                return
            except OSError as e:
                print("WsWemos connect - MQTT can't connect", e)
                time.sleep(1)

    def ping(self):
        self.c.ping()

    # Received messages from subscriptions will be delivered to this callback
    def sub(self, topic, msg):
        print('WsWemos sub')
        print(topic, msg)
        payload = json.loads(msg)
        print(payload)
        if topic == self.devicename + b"/to_device/switch":
            switchvalue = payload['value']
            print("Schalter: ", switchvalue)
            if switchvalue == 'on':
                self.switch = machine.Pin(self.PIN_RELAY, machine.Pin.OUT)
                self.switch.value(0)
                self.switchstatus = 'on'
                self.pinLED.value(0)
                self.ledstatus = 'on'
            else:
                self.switch = machine.Pin(self.PIN_RELAY, machine.Pin.IN)
                self.switchstatus = 'off'
                self.pinLED.value(1)
                self.ledstatus = 'off'

            self.send_status(payload)
        elif topic == self.devicename + b"/to_device/command":
            command = payload['value']
            print('command: ', command)
            if command == 'reset':
                machine.reset()
            elif command == 'setdevicename':
                self.devicename = payload['name'].encode()
                try:
                    f = open('devicename.config', 'w')
                    f.write(self.devicename)
                    f.close()
                except Exception as e:
                    print("WsWemos - sub: Error writing devicename %s", e)

                self.send_status(payload)
            elif command == 'exit':
                sys.exit()
                # elif topic == self.devicename + b"/to_device/LED":
                #     ledvalue = payload['value']
                #     if ledvalue == 'on':
                #         self.pinLED.value(0)
                #         self.ledstatus = 'on'
                #     else:
                #         self.pinLED.value(1)
                #         self.ledstatus = 'off'

            self.send_status(payload)
        elif topic == self.devicename + b"/to_device/status":
            self.send_status(payload)

    def send_status(self, payload):
        payload['free_mem'] = gc.mem_free()
        payload['switchstatus'] = self.switchstatus
        payload['ledstatus'] = self.ledstatus
        payload['mac'] = self.mac
        self.c.publish(self.devicename + b"/from_device/status", json.dumps(payload))

    def checkMessage(self):
        if time.ticks_diff(self.startticks,
                           time.ticks_ms()) > 10000 or self.startticks >= time.ticks_ms():  # alle 10 Sekunden und bei Überlauf
            self.ping()
            self.startticks = time.ticks_ms()
            print("WsWemos - checkMessage - send ping. Time: %s", self.startticks)

        self.c.check_msg()
