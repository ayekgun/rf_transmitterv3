import os
import sys
import Transmitter
import requests
import json
import urllib
import time
import datetime
import hashlib

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultSOIP():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiSOIP()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_account
            global t_time
            global t_sign
            global t_phones
            global t_senderId
            global t_content
            global t_smsType
            global t_responetrxid


            t_account = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['account'][0])
            t_time = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['time'][0])
            t_sign = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['sign'][0])
            t_phones = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['phones'][0])
            t_senderId = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['senderId'][0])
            t_content = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['content'][0])
            t_smsType = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['smsType'][0])
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiSOIP():
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

def CheckValueTelcoAccount():
	str1 = "account From Config ="
	str2 = "account From Telco ="
	result =Transmitter.MetchingData(Transmitter.cfg_account, t_account, str1, str2)
	return(result)


def CheckValueTelcoTime():
    timestamp = int(time.time())
    telco_timestamp = datetime.datetime.fromtimestamp(int(t_time) / 1000)
    current_timestamp = datetime.datetime.fromtimestamp(timestamp)

    if telco_timestamp - datetime.timedelta(minutes=5) <= current_timestamp <= telco_timestamp + datetime.timedelta(minutes=5):
        x = t_time
    else:
        x = "selisih waktu 5 menit"

    str1 = "time From Queue ="
    str2 = "time From Queue / Table  ="
    result =Transmitter.MetchingData(x, t_time, str1, str2)
    return(result)


def CheckValueTelcoSign():
    key = str(t_time)+str(Transmitter.cfg_account)+(Transmitter.cfg_secret_key)
    data = key.encode('utf-8')
    md5 = hashlib.md5()    
    md5.update(data)
    gen_sign = md5.hexdigest()
    str1 = "sign From Queue ="
    str2 = "sign From Queue / Table  ="
    result =Transmitter.MetchingData(str(gen_sign), t_sign, str1, str2)
    return(result)


def CheckValueTelcoPhones():    
	str1 = "phones From Queue ="
	str2 = "phones From Queue / Table  ="
	result =Transmitter.MetchingData(Transmitter.quinmsisdn, t_phones, str1, str2)
	return(result)


def CheckValueTelcoSenderid():
    str1 = "senderId From Queue ="
    str2 = "senderId From Queue / Table  ="
    if(Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_senderid != ''):
            c_sid = Transmitter.sid_queue_senderid
        else:
            c_sid = ''
    else:
        if(Transmitter.quinsenderid != ''):
            c_sid = Transmitter.quinsenderid
        else:
            c_sid = ''
    result = Transmitter.MetchingData(c_sid, t_senderId, str1, str2)
    return (result)


def CheckValueTelcoContent():
	str1 = "content From Queue ="
	str2 = "content From Queue / Table  ="
	result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), t_content, str1, str2)
	return(result)


def CheckValueTelcoSmstype():
    if Transmitter.quinservicetype == "OTP":
        gen_smsType = '1'
    else:
        gen_smsType = '2'
    str1 = "smsType From Queue ="
    str2 = "smsType From Queue / Table  ="
    result =Transmitter.MetchingData(gen_smsType, t_smsType, str1, str2)
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
