import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultBhramayasa():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiBhramayasa()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_user
            global t_password
            global t_sender
            global t_msisdn
            global t_message
            global t_desc
            global t_dlr
            global t_responetrxid

            t_user = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['username'][0])
            t_password = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['password'][0])
            t_sender = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['sourceaddr'][0])
            t_msisdn = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['destinationaddr'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['shortmessage'][0])
            t_desc = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['desc'][0])
            t_dlr = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['dlr'][0])
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiBhramayasa():
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

def CheckVallueUsernameBhramayasa():
    str1 = "Username From DB Config"
    str2 = "Username In TelcoReceiver"
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
    result = Transmitter.MetchingData(c_uid, t_user, str1, str2)
    return (result)


def CheckValluePasswordBhramayasa():
    str1 = "Password From DB Config"
    str2 = "Password In TelcoReceiver"
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
    result = Transmitter.MetchingData(c_pwdtelco, t_password, str1, str2)
    return (result)


def CheckVallueSourceAddrBhramayasa():
    str1 = "Sender From Queue/DB Config"
    str2 = "Sender In TelcoReceiver"
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
    result = Transmitter.MetchingData(c_sid, t_sender, str1, str2)
    return (result)


def CheckVallueDestinationAddrBhramayasa():
    str1 = "Msisdn From Queue"
    str2 = "Msisdn In TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return (result)


def CheckVallueShortMessageBhramayasa():
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)


def CheckVallueDescBhramayasa():
    str1 = "Desc From DB Config"
    str2 = "Desc From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinadddata1, t_desc, str1, str2)
    return (result)


def CheckVallueDlrBhramayasa():
    str1 = "DLR From DB Config"
    str2 = "DLR From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinadddata2, t_dlr, str1, str2)
    return (result)


def CallBhramayasaResponStatus():
    if t_responetrxid.startswith("SENT"):
        return "0"
    else:
        return t_responetrxid


def CallBhramayasaResponTrxid():
    return t_responetrxid
