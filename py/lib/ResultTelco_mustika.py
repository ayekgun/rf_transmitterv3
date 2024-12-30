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


def SetVariableResponeResultMustika():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiMustika()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_id
            global t_message
            global t_productid
            global t_trxdate
            global t_trxid
            global t_userid
            global t_header_content_type
            global t_header_auth
            global t_header_apikey

            
            parsed_header_data = json.loads(json_data['header'])
            t_header_content_type = parsed_header_data.get('Content-Type')
            t_header_auth = parsed_header_data.get('Authorization')
            t_header_apikey = parsed_header_data.get('X-API-KEY')

            # Extract information
            json_load = json.loads(json_data['parameter'])['smsgwRq']
            t_userid = json_load['userid']
            t_trxid = json_load['trxid']
            t_productid = json_load['productid']
            t_id = json_load['id']
            t_message = json_load['message']
            t_trxdate = json_load['trxdate']

            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiMustika():
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

def CheckVallueIdTelcoMustika():
    str1 = "Msisdn / Recipient From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_id, str1, str2)
    return (result)


def CheckVallueProductIDTelcoMustika():
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
    result = Transmitter.MetchingData(c_sid, t_productid, str1, str2)
    return (result)


def CheckVallueMessageTelcoMustika():
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)


def CheckVallueTrxDateMustika():

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

def CheckVallueUserIdMustika():
    str1 = "User ID From DB Config"
    str2 = "User Id In TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username != ''):
            c_cpname = Transmitter.sid_queue_username
        else:
            c_cpname = Transmitter.cfg_uid
    else:
        if(Transmitter.quinuid != ''):
            c_cpname = Transmitter.quinuid
        else:
            c_cpname = Transmitter.cfg_uid
    result = Transmitter.MetchingData(c_cpname, t_userid, str1, str2)
    return (result)



def CheckVallueHeaderContentTypeMustika():
    std_content_type = 'application/json; charset=utf-8'
    str1 = "Content Type Standard ",std_content_type
    str2 = "Content Type In Header Dummy Result API = ", t_header_content_type
    result = Transmitter.MetchingData(std_content_type,  t_header_content_type, str1, str2)
    return(result)

def CheckVallueHeaderAuthMustika():
    str1 = "Expected Auth From Generate"
    str2 = "Auth From TelcoReceiver"

    # Pemilihan username dan password berdasarkan konfigurasi
    if Transmitter.senderids_support == 'true':
        username = Transmitter.sid_queue_username if Transmitter.sid_queue_username else Transmitter.cfg_uid
        password = Transmitter.sid_queue_password if Transmitter.sid_queue_password else Transmitter.cfg_pwd
    else:
        username = Transmitter.quinuid if Transmitter.quinuid else Transmitter.cfg_username
        password = Transmitter.quinpwd if Transmitter.quinpwd else Transmitter.cfg_password
    # username = Transmitter.cfg_uid
    # password = Transmitter.cfg_pwd

    # Membuat nilai Authorization
    credentials = f"{password}:{username}"
    base64_encoded = base64.b64encode(credentials.encode()).decode()

    # SHA256 hashing
    hashed_auth = hashlib.sha256(base64_encoded.encode()).hexdigest()

    # Menambahkan prefix "Basic"
    Auth = f"Basic {hashed_auth}"
    # Pencocokan hasil dengan nilai di header
    print(Auth)
    print(t_header_auth)
    result = Transmitter.MetchingData(Auth, t_header_auth, str1, str2)
    return result

def CheckValueXApiKeyMustika():
    str1 = "Expected X-API-KEY From Generate"
    str2 = "X-API-KEY From TelcoReceiver"

    # Mengambil nilai konfigurasi dari Transmitter
    token = Transmitter.cfg_token if Transmitter.cfg_token else ''

    # Membuat nilai X-API-KEY
    input_string = f"{token}{t_trxdate}{t_id}"
    computed_x_api_key = hashlib.sha256(input_string.encode()).hexdigest()

    # Pencocokan nilai dengan header dari TelcoReceiver
    result = Transmitter.MetchingData(computed_x_api_key, t_header_apikey, str1, str2)
    return result

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
