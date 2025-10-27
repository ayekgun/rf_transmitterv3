import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultJantara():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiJantara()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            
            global t_message
            global t_respontrxid
            global t_responstatus
            global t_username
            global t_password
            global t_command
            global t_ani
            global t_dnis
            global t_dataCoding
            global t_longMessageMode
            
            # Parse new JSON parameters
            t_username = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['username'][0])
            t_password = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['password'][0])
            t_command = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['command'][0])
            t_ani = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['ani'][0])
            t_dnis = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['dnis'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['message'][0])
            t_dataCoding = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True).get('dataCoding', [None])[0])
            t_longMessageMode = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True).get('longMessageMode', [None])[0])
            t_respontrxid = json_data['provider_trxid']
            t_responstatus = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiJantara():
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

def CheckVallueANITelcoJantara():
    str1 = "ANI From DB Config"
    str2 = "ANI From TelcoReceiver"
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
    result = Transmitter.MetchingData(c_sid, t_ani, str1, str2)
    return (result)


def CheckVallueDataCodingTelcoJantara():
    str1 = "Data Coding From DB Expected"
    str2 = "Data Coding From TelcoReceiver Actual"
    # If t_dataCoding is None or empty, convert to empty string
    expected_value = None  # Expected value bisa None jika tidak dikirim
    actual_value = t_dataCoding if t_dataCoding is not None else None
    result = Transmitter.MetchingData(expected_value, actual_value, str1, str2)
    return (result)

def CheckVallueDNISTelcoJantara():
    str1 = "DNIS From Queue"
    str2 = "DNIS From TelcoReceiver"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_dnis, str1, str2)
    return (result)

def CheckVallueLongMessageModeTelcoJantara():
    str1 = "Long Message Mode From DB Expected"
    str2 = "Long Message Mode From TelcoReceiver Actual"
    # If t_longMessageMode is None or empty, convert to empty string
    expected_value = None  # Expected value bisa None jika tidak dikirim
    actual_value = t_longMessageMode if t_longMessageMode is not None else None
    result = Transmitter.MetchingData(expected_value, actual_value, str1, str2)
    return (result)


def CheckVallueMessageTelcoJantara():
    str1 = "Message From DB Config"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return (result)


def CheckVallueCommandTelcoJantara():
    str1 = "Command From DB Expected"
    str2 = "Command From TelcoReceiver Actual"
    result = Transmitter.MetchingData("submit", t_command, str1, str2)
    return (result)

def CheckVallueUsernameTelcoJantara():
    str1 = "Username From DB Config"
    str2 = "Username From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username != ''):
            c_username = Transmitter.sid_queue_username
        else:
            c_username = Transmitter.cfg_username
    else:
        if(Transmitter.quinuid != ''):
            c_username = Transmitter.quinuid
        else:
            c_username = Transmitter.cfg_username
    result = Transmitter.MetchingData(c_username, t_username, str1, str2)
    return (result)


def CheckValluePasswordTelcoJantara():
    str1 = "Password From DB Config"
    str2 = "Password From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_password != ''):
            c_password = Transmitter.sid_queue_password
        else:
            c_password = Transmitter.cfg_password
    else:
        if(Transmitter.quinpwd != ''):
            c_password = Transmitter.quinpwd
        else:
            c_password = Transmitter.cfg_password
    result = Transmitter.MetchingData(c_password, t_password, str1, str2)
    return (result)

def CallJantaraProviderTrxid():
    return (t_respontrxid)

def CallJantaraResponStatus():
    return(t_responstatus)
#end check hit Telco
