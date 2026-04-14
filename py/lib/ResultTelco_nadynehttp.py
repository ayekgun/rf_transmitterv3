import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultNadyneHttp():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiNadyneHttp()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_user
            global t_pwd
            global t_sender
            global t_msisdn
            global t_message
            global t_respontrxid
            global t_responstatus


            t_user = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['user'][0])
            t_pwd = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['pwd'][0])
            t_sender = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['sender'][0])
            t_msisdn = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['msisdn'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['message'][0])
            t_respontrxid = json_data['provider_trxid']
            t_responstatus = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiNadyneHttp():
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

def CheckVallueUserNadyneTelco():
    str1 = "User / Recipient From Queue"
    str2 = "User From TelcoReceiver"
    #standard Pengecekan di comment
    # if (Transmitter.senderids_support == 'true'):
    #     if(Transmitter.sid_queue_cpname != ''):
    #         c_cpname = Transmitter.sid_queue_cpname
    #     else:
    #         c_cpname = Transmitter.cfg_username
    # else:
    #     if(Transmitter.quincpName != ''):
    #         c_cpname = Transmitter.quincpName
    #     else:
    #         c_cpname = Transmitter.cfg_username
    result = Transmitter.MetchingData(Transmitter.cfg_provider_username, t_user, str1, str2)
    return (result)

def CheckValluePwdNadyneTelco():
    str1 = "Password / Recipient From Queue"
    str2 = "Password From TelcoReceiver"
    #standard Pengecekan di comment
    # if (Transmitter.senderids_support == 'true'):
    #     if(Transmitter.sid_queue_password != ''):
    #         c_pwdtelco = Transmitter.sid_queue_password
    #     else:
    #         c_pwdtelco = Transmitter.cfg_password
    # else:
    #     if(Transmitter.quinpwd != ''):
    #         c_pwdtelco = Transmitter.quinpwd
    #     else:
    #         c_pwdtelco = Transmitter.cfg_password
    result = Transmitter.MetchingData(Transmitter.cfg_provider_password, t_pwd, str1, str2)
    return (result)


def CheckVallueSenderNadyneTelco():
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
    result = Transmitter.MetchingData(c_sid, t_sender, str1, str2)
    return (result)


def CheckVallueMessageNadyneTelco():
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)

def CheckVallueMsisdnNadyneTelco():
    str1 = "Msisdn / Recipient From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return (result)

def CallNaydneProviderTrxid():
    return (t_respontrxid)

def CallNadyneResponStatus():
    return(t_responstatus)
# def CheckVallueResponTrxidTelco():
#     str1 = "Msisdn / Recipient From Queue"
#     str2 = "Msisdn From TelcoReceiver"
#     result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_respontrxid, str1, str2)
#     return (result)

# def CheckVallueResponStatusTelco():
#     str1 = "Msisdn / Recipient From Queue"
#     str2 = "Msisdn From TelcoReceiver"
#     result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_responstatus, str1, str2)
#     return (result)
#end check hit Telco
