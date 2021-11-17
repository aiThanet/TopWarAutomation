from ppadb.client import Client as AdbClient
import utils

adbClient = AdbClient(host='127.0.0.1', port=5037)
devices = adbClient.devices()
# print(devices)
device = devices[0]

for i in range(1000):
    utils.click(device, 460, 2180,'',0.00001)
