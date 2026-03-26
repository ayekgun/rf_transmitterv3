import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultTelkomsel():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiTelkomsel()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_appsid
            global t_msisdn
            global t_pwd
            global t_sid
            global t_sms
            global t_responetrxid
            
            # TelkomselHttpHandlerImpl.java only sends 6 parameters: appsid, pwd, sid, trx_id, msisdn, sms
            # Replace ';' with '%3B' (URL encoded semicolon) before parsing to prevent parse_qs from splitting at ';'
            temp_param = json_data['parameter'].replace(';', '%3B')
            params = urllib.parse.parse_qs(temp_param, keep_blank_values=True)
            
            t_appsid = params['appsid'][0] if 'appsid' in params else ''
            t_msisdn = params['msisdn'][0] if 'msisdn' in params else ''
            t_pwd = params['pwd'][0] if 'pwd' in params else ''
            t_sid = params['sid'][0] if 'sid' in params else ''
            t_sms = params['sms'][0] if 'sms' in params else ''
            
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiTelkomsel():
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

    return result

def CheckVallueAppidTelkomsel():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username != ''):
            c_uid = Transmitter.sid_queue_username
        else:
            c_uid = Transmitter.cfg_username
    else:
        if(Transmitter.quinuid != ''):
            c_uid = Transmitter.quinuid
        else:
            c_uid = Transmitter.cfg_username
    result = Transmitter.MetchingData(c_uid, t_appsid, str1, str2)
    return (result)


def CheckVallueMsisdnTelkomsel():
    str1 = "Msisdn From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return (result)


def CheckValluePwdTelkomsel():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
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
    result = Transmitter.MetchingData(c_pwdtelco, t_pwd, str1, str2)
    return (result)


def CheckVallueSidTelkomsel():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
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
    result = Transmitter.MetchingData(c_sid, t_sid, str1, str2)
    return (result)


def CheckVallueSMSTelkomsel():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_sms), str1, str2)
    return (result)

# Note: cp_name and trx_date checks removed as they are not sent by TelkomselHttpHandlerImpl.java

#end check hit Telco
