import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultModify():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiModify()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_senderid
            global t_is_unicode
            global t_is_flash
            # global t_schedtime
            # global t_groupid
            global t_message
            global t_mobilenumber
            global t_apikey
            global t_clientid
            global t_respontrxid
            global t_responstatus
            
            t_senderid = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['senderid'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['message'][0])
            t_is_unicode = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['is_unicode'][0])
            t_is_flash = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['is_flash'][0])
            # t_schedtime = (urllib.parse.parse_qs(
            #     json_data['parameter'], keep_blank_values=True)['schedtime'][0])
            # t_groupid = (urllib.parse.parse_qs(
            #     json_data['parameter'], keep_blank_values=True)['groupid'][0])
            t_mobilenumber = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['mobilenumber'][0])
            t_apikey = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['apikey'][0])
            print(t_apikey)
            t_clientid = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['clientid'][0])
            t_respontrxid = json_data['provider_trxid']
            t_responstatus = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiModify():
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

def CheckVallueSenderIDTelcoModify():
    str1 = "Sender ID From DB Config"
    str2 = "Sender ID From TelcoReceiver"
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


def CheckVallueIsUnicodeTelcoModify():
    str1 = "Is Unicode From DB Config"
    str2 = "Is Unicode From TelcoReceiver"
    if(t_is_unicode == ''):
        is_unicode_conv = 'false'
    elif(t_is_unicode == '1'):
        is_unicode_conv = 'true'
    else:
        is_unicode_conv = 'mot found'
    result = Transmitter.MetchingData(Transmitter.cfg_is_unicode, is_unicode_conv, str1, str2)
    return (result)


def CheckVallueMobileNumberTelcoModify():
    str1 = "Msisdn From Queue"
    str2 = "Msisdn From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_mobilenumber, str1, str2)
    return (result)


def CheckVallueApiKeyTelcoModify():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    # convapikey = urllib.parse.urlencode(str(t_apikey))
    # print(convapikey)
    # if (senderids_support == 'true'):
    #     if(Transmitter.sid_queue_password != ''):
    #         c_pwdtelco = Transmitter.sid_queue_password
    #     else:
    #         c_pwdtelco = Transmitter.cfg_password
    # else:
    #     if(Transmitter.quinpwd != ''):
    #         c_pwdtelco = Transmitter.quinpwd
    #     else:
    #         c_pwdtelco = Transmitter.cfg_password
    result = Transmitter.MetchingData(Transmitter.cfg_api_key, t_apikey.replace(" ", "+") , str1, str2)
    return (result)


def CheckVallueIsFlashTelcoModify():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    if(t_is_flash == ''):
        t_is_flash_conv = 'false'
    elif(t_is_flash == '1'):
        t_is_flash_conv = 'true'
    else:
        t_is_flash_conv = 'mot found'
    result = Transmitter.MetchingData(Transmitter.cfg_is_flash, t_is_flash_conv, str1, str2)
    return (result)


def CheckVallueMessageTelcoModify():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)


def CheckVallueScheduledTimeTelcoModify():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.cfg_username, Transmitter.cfg_username, str1, str2)
    return (result)

def CheckVallueGroupTelcoModify():
    str1 = "Appid From DB Config"
    str2 = "Appid From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.cfg_username, Transmitter.cfg_username, str1, str2)
    return (result)

def CheckVallueClientIDTelcoModify():
    str1 = "Sender ID From DB Config"
    str2 = "Sender ID From TelcoReceiver"
    # if (Transmitter.senderids_support == 'true'):
    #     if(Transmitter.sid_queue_username != ''):
    #         c_uid = Transmitter.sid_queue_username
    #     else:
    #         c_uid = Transmitter.cfg_username
    # else:
    #     if(Transmitter.quinuid != ''):
    #         c_uid = Transmitter.quinuid
    #     else:
    #         c_uid = Transmitter.cfg_username
    result = Transmitter.MetchingData(Transmitter.cfg_client_id, t_clientid, str1, str2)
    return (result)

def CallModifyProviderTrxid():
    return (t_respontrxid)

def CallModifyResponStatus():
    return(t_responstatus)
#end check hit Telco
