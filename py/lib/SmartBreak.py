import os
import sys
import Transmitter
import requests
import time
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath("py/conf"))
# from conf_tsel import *
from config import *


def CheckConsumerQueue(message):
    time.sleep(int(Transmitter.cfg_sleep_after_send) / 1000)
    time.sleep(2)
    req = requests.get(urlqueuejsp, auth=('admin', 'admin'))
    xmldata = req.text
    root = ET.fromstring(xmldata)
    root = root.find("./queue/.[@name='" + Transmitter.queuename + "']/stats")
    consumer = root.attrib['consumerCount']
    if (message == 'break'):
        expconsumer = 0
    else:
        expconsumer = 1
    str1 = "Consumer Actual = "
    str2 = "Expected Consumer = "
    result = Transmitter.MetchingData(int(consumer), expconsumer, str1, str2)
    return (result)
