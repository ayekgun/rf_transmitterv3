import os
import sys
import Transmitter
import requests
import json
import urllib
import time
import base64

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultPintar():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiPintar()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_senderid
            global t_type
            global t_msisdn
            global t_message
            global t_username
            global t_password
            global t_token
            global t_callbackurl
            global t_callbackmethod
            global t_encoding
            global t_header_content_type
            global t_header_auth

            json_load = json.loads(json_data['parameter'])
            parsed_header_data = json.loads(json_data['header'])
            t_header_content_type = parsed_header_data.get('Content-Type')
            t_header_auth = parsed_header_data.get('Authorization')

            # Extract information
            t_senderid = json_load['messages'][0]['senderid']
            t_type = json_load['messages'][0]['type']
            t_msisdn = json_load['messages'][0]['msisdn']
            t_encoding = json_load['messages'][0]['encoding']
            t_message = json_load['messages'][0]['message']
            t_username = json_load['messages'][0]['username']
            t_password = json_load['messages'][0]['password']
            t_token = json_load['messages'][0]['token']
            t_callbackurl = json_load['messages'][0]['callbackurl']
            t_callbackmethod = json_load['messages'][0]['callbackmethod']

            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiPintar():
    n = 1
    while n <= 3:
        url = urlcekresult + str(Transmitter.generatediddash)
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

def CheckVallueToTelco():
    str1 = "Msisdn / Recipient From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_type, str1, str2)
    return (result)


def CheckVallueFromTelco():
    str1 = "Sender From Queue"
    str2 = "Sender From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_senderid != ''):
            c_sid = Transmitter.sid_queue_senderid
        else:
            c_sid = ''
    else:
        if(Transmitter.quinsenderid != ''):
            c_sid = Transmitter.quinsenderid
        else:
            c_sid = ''
    result = Transmitter.MetchingData(c_sid, t_senderid, str1, str2)
    return (result)


def CheckVallueTextTelco():
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_msisdn), str1, str2)
    return (result)


def CheckVallueNotifyUrlTelco():
    str1 = "notify_url Id From Config"
    str2 = "notify_url Id From TelcoReceiver"
    result = Transmitter.MetchingData(
        (Transmitter.cfg_notify_url), t_encoding, str1, str2)
    return (result)

def CheckVallueHeaderContentType():
    std_content_type = 'application/json'
    str1 = "Content Type Standard ",std_content_type
    str2 = "Content Type In Header Dummy Result API = ", t_header_content_type
    result = Transmitter.MetchingData(std_content_type,  t_header_content_type, str1, str2)
    return(result)

def CheckVallueHeaderAuth():
    str1 = "Auth From DB Config"
    str2 = "Auth From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username == ''):
            username = Transmitter.cfg_username
        else:
            username = Transmitter.sid_queue_username
        if(Transmitter.sid_queue_password == ''):
            password = Transmitter.cfg_password
        else:
            password = Transmitter.sid_queue_password
        credentials = f"{username}:{password}"
    else:
        if(Transmitter.quinuid == ''):
            username = Transmitter.cfg_username
        else:
            username = Transmitter.quinuid
        if(Transmitter.quinpwd == ''):
            password = Transmitter.cfg_password
        else:
            password = Transmitter.quinpwd
        credentials = f"{username}:{password}"
    Auth = base64.b64encode(credentials.encode()).decode()
    Auth = f'Basic {Auth}'
    result = Transmitter.MetchingData(Auth, t_header_auth, str1, str2)
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


#end check hit Telco
