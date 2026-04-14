import os
import sys
import Transmitter
import requests
import json
import urllib
import time
import base64
import hashlib
from datetime import datetime
sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultM360():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiM360()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_app_key
            global t_app_secret
            global t_msisdn
            global t_content
            global t_shortcode_mask
            global t_rcvd_transid
            global t_is_intl
            
            # parsed_header_data = json.loads(json_data['header'])
            # t_header_content_type = parsed_header_data.get('Content-Type')
            # t_header_auth = parsed_header_data.get('Authorization')
            # t_header_apikey = parsed_header_data.get('X-API-KEY')

            # Extract information
            data = json.loads(json_data)
            t_app_key = data["app_key"]
            t_app_secret = data["app_secret"]
            t_msisdn = data["msisdn"]
            t_content = data["content"]
            t_shortcode_mask = data["shortcode_mask"]
            t_rcvd_transid = data["rcvd_transid"]
            t_is_intl = data["is_intl"]

            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiM360():
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


def CheckValueTelcoApp_KeyM360():
    str1 = "App Key From Generate Robot"
    str2 = "App Key From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username != ''):
            c_cpname = Transmitter.sid_queue_username
        else:
            c_cpname = Transmitter.cfg_username
    else:
        if(Transmitter.quinuid != ''):
            c_cpname = Transmitter.quinuid
        else:
            c_cpname = Transmitter.cfg_username
    result = Transmitter.MetchingData(c_cpname, t_app_key, str1, str2)
    return (result)

def CheckValueTelcoApp_SecretM360():
    str1 = "App Secret / Recipient From Queue"
    str2 = "App Secret From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_password != ''):
            c_pwdtelco = Transmitter.sid_queue_password
        else:
            c_pwdtelco = Transmitter.cfg_password
    else:
        if(Transmitter.quinpwd != ''):
            c_pwdtelco = Transmitter.quinpwd
        else:
            c_pwdtelco = Transmitter.cfg_password
    result = Transmitter.MetchingData(c_pwdtelco, t_app_secret, str1, str2)
    return (result)

def CheckValueTelcoMsisdnM360():
    str1 = "Msisdn / Recipient From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn , str1, str2)
    return(result)

def CheckValueTelcoContentM360():
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_content), str1, str2)
    return (result)

def CheckValueTelcoRcvd_TransidM360():
    str1 = "rcvd_transid From Queue"
    str2 = "rcvd_transid From Queue / Table"
    result = Transmitter.MetchingData("", t_rcvd_transid, str1, str2)
    return(result)

def CheckValueTelcoIs_IntlM360():
    str1 = "is_intl From Queue"
    str2 = "is_intl From Queue / Table"
    result = Transmitter.MetchingData("False", t_is_intl, str1, str2)
    return(result)  

def CheckValueTelcoShortcode_MaskM360():
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
    result = Transmitter.MetchingData(c_sid, t_shortcode_mask, str1, str2)
    return (result)


def CheckVallueTrxDateM360():

    try:
        # Mencoba untuk mem-parsing trxdate sesuai format yang diinginkan
        datetime.strptime(t_trxdate, "%Y%m%d%H%M%S")
        data = {
            "status": "OK",
            "message": "Format TrxDate sesuai"
        }
        return data
    except ValueError:
        # Jika format tidak sesuai, akan memunculkan ValueError
        data = {
            "status": "NOK",
            "message": "Format TrxDate tidak sesuai"
        }
        return data





def CheckVallueHeaderContentTypeM360():
    std_content_type = 'application/json; charset=utf-8'
    str1 = "Content Type Standard ",std_content_type
    str2 = "Content Type In Header Dummy Result API = ", t_header_content_type
    result = Transmitter.MetchingData(std_content_type,  t_header_content_type, str1, str2)
    return(result)

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
