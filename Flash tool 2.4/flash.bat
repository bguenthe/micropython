c:\python27\python c:\python27\Scripts\esptool.py --port COM4 erase_flash

c:\python27\python c:\python27\Scripts\esptool.py --port COM4 write_flash -fm dio -fs 32m -ff 40m 0x0000000 esp8266-20160904-v1.8.3-101-g015774a.bin