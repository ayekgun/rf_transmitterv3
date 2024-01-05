import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultMitracomm():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiMitracomm()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_refno
            global t_user
            global t_msisdn
            global t_password
            global t_masking
            global t_message
            global t_respontrxid
            global t_responstatus


            t_refno = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['refno'][0])
            t_user = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['userid'][0])
            t_msisdn = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['msisdn'][0])
            t_password = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['password'][0])
            t_masking = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['masking'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['message'][0])
            t_respontrxid = (urllib.parse.parse_qs(
                json_data['respon'], keep_blank_values=True)['refno'][0])
            t_responstatus = (urllib.parse.parse_qs(
                json_data['respon'], keep_blank_values=True)['status'][0])
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiMitracomm():
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

def CheckVallueUserIdMitracomm():
    str1 = "User ID From DB Config"
    str2 = "User Id In TelcoReceiver"
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
    result = Transmitter.MetchingData(c_cpname, t_user, str1, str2)
    return (result)


def CheckVallueMsisdnTelcoMitracomm():
    str1 = "Msisdn From Queue"
    str2 = "Msisdn In TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return (result)


def CheckValluePasswordTelcoMitracomm():
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


def CheckVallueMaskinTelcoMitracomm():
    str1 = "Masking From DB Config"
    str2 = "Masking In TelcoReceiver"
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
    result = Transmitter.MetchingData(c_sid, t_masking, str1, str2)
    return (result)


def CheckVallueMessageTelcoMitracomm():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)


def CheckValluRefnoTelcoMitracomm():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(t_respontrxid, t_refno, str1, str2)
    return (result)

def CheckValluSuffixRefnoTelcoMitracomm():
    str1 = "Suffix RefNo in Config"
    str2 = "Suffix RefNo From TelcoReceiver"
    g_suffix = t_refno.endswith('_0')
    if(g_suffix == True):
        suffix = '_0'
    else:
        suffix = ''
    result = Transmitter.MetchingData('_0', suffix, str1, str2)
    return (result)

def CallMitracommResponStatus():
    return t_responstatus
    
def CallMitracommResponTrxid():
    return t_respontrxid
    pass

#end check hit Telco
