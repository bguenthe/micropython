import json
import time
from datetime import datetime

import paho.mqtt.client as mqtt

client = None


# def on_connect(client, userdata, flags, rc):
#     print(get_time() + ": " + "Connected with result code " + str(rc))
#
#     topics = [("/raspberry/howareyou", 0), ]
#
#     client.subscribe(topics)
#     print(get_time() + ": " + "Subscribed to: " + str(topics))


def mqtt_init():
    global client
    client = mqtt.Client()
    # client.on_connect = on_connect
    client.connect("192.168.178.35", 1883, 60)


def get_time():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


if __name__ == "__main__":
    connected = False
    while not connected:
        try:
            mqtt_init()
            connected = True
            client.loop_start()
            i = 0
            payload = {}
            switchstatus = "off"
            while True:
                if switchstatus == "off":
                    switchstatus = "on"
                else:
                    switchstatus = "off"

                i += 1
                payload['value'] = switchstatus
                payload['counter'] = str(i)

                #client.publish("to_devive/broadcast/staus", json.dumps(payload))
                client.publish("wemos01/to_device/switch", json.dumps(payload))
                client.publish("wemos02/to_device/switch", json.dumps(payload))
                print(json.dumps(payload))
                time.sleep(60)  # jede Minute
        except Exception as e:
            print(get_time() + ": " + e.__str__())
            connected = False
            time.sleep(5)
