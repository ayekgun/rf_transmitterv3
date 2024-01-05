import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultTsel():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiTsel()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_appsid
            global t_cp_name
            global t_msisdn
            global t_pwd
            global t_sid
            global t_sms
            global t_trx_date
            global t_responetrxid
            
            t_appsid = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['appsid'][0])
            t_cp_name = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['cp_name'][0])
            t_msisdn = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['msisdn'][0])
            t_pwd = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['pwd'][0])
            t_sid = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['sid'][0])
            t_sms = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['sms'][0])
            t_trx_date = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['trx_date'][0])
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiTsel():
    n = 1
    while n <= 3:
        url = urlcekresult + 'jts-'+str(Transmitter.generatediddash).replace('-', '')
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

def CheckVallueAppidTelco():
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


def CheckVallueCp_NameTelco():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_cpname != ''):
            c_cpname = Transmitter.sid_queue_cpname
        else:
            c_cpname = Transmitter.cfg_username
    else:
        if(Transmitter.quincpName != ''):
            c_cpname = Transmitter.quincpName
        else:
            c_cpname = Transmitter.cfg_username
    result = Transmitter.MetchingData(c_cpname, t_cp_name, str1, str2)
    return (result)


def CheckVallueMsisdnTelco():
    str1 = "Msisdn From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return (result)


def CheckValluePwdTelco():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    if (senderids_support == 'true'):
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


def CheckVallueSidTelco():
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


def CheckVallueSMSTelco():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_sms), str1, str2)
    return (result)


def CheckValluTrx_DateTelco():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.cfg_username, Transmitter.cfg_username, str1, str2)
    return (result)

#end check hit Telco
