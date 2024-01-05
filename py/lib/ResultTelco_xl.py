import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultXL():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiXL()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_recipient
            global t_msg_id
            global t_sender
            global t_encoding
            global t_message
            global t_responetrxid

            t_recipient = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['recipient'][0])
            t_msg_id = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['msg_id'][0])
            t_sender = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['sender'][0])
            t_encoding = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['encoding'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['message'][0])
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiXL():
    n = 1
    while n <= 3:
        url = urlcekresult + 'jts-'+str(Transmitter.generatediddash)
        req = requests.get(url)
        json_data = json.loads(req.text)
        n += 1
        if(json_data == 'Data Not Found'):
            print(url)
            result = json_data
            time.sleep(2)
        else:
            result = json_data
            break

    # print(result)
    print(result)
    return result

def CheckVallueRecipientTelco():
    str1 = "Msisdn / Recipient From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_recipient, str1, str2)
    return (result)


def CheckVallueSenderTelco():
    str1 = "Sender From Queue"
    str2 = "Sender From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(sid_queue_senderid != ''):
            c_sid = sid_queue_senderid
        else:
            c_sid = ''
    else:
        if(Transmitter.quinsenderid != ''):
            c_sid = Transmitter.quinsenderid
        else:
            c_sid = ''
    result = Transmitter.MetchingData(c_sid, t_sender, str1, str2)
    return (result)


def CheckVallueMessageTelco():
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)


def CheckValluMsgIdTelco():
    str1 = "Msg Id From Queue"
    str2 = "Msg Id From TelcoReceiver"
    result = Transmitter.MetchingData(
        'jts-'+str(Transmitter.generatediddash), t_msg_id, str1, str2)
    return (result)


def CheckIntervalHit():
    str1 = "First Hit Time"
    str2 = "Second Hit time"
    if(CheckFlowToTelco() == 'expired' or CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        if (retryable == 'true'):
            x = GetResultDummyWithDB()
            array = list()
            for row in x:
                array.append(row[4])
            time1 = array[0]
            time2 = array[1]
            time3 = time2 - timedelta(seconds=(int(cfg_RETRY_TIMEOUT) / 1000))
            result = Transmitter.MetchingData(time1, time3, str1, str2)
        else:
            result = Transmitter.MetchingData(
                'NO Retry', 'NO Retry', str1, str2)
    return (result)


def CheckTotalRetryHit():
    str1 = "Config Retry In DB"
    str2 = "Total Hit In Telco"
    if(CheckFlowToTelco() == 'expired' or CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        if (retryable == 'true'):
            x = GetResultDummyWithDB()
            x = len(x)
            result = Transmitter.MetchingData(
                int(cfg_max_retry)+1, int(x), str1, str2)
        else:
            result = Transmitter.MetchingData(
                'NO Retry', 'NO Retry', str1, str2)
    return (result)


def CheckValluEncodingTelco():
    str1 = "Encoding From DB Config"
    str2 = "Encoding From TelcoReceiver"
    result = Transmitter.MetchingData('0', t_encoding, str1, str2)
    return (result)
#end check hit Telco
