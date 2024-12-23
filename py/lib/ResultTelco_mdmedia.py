import os
import sys
import Transmitter
import requests
import json
import urllib
import time
import base64

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultMdmedia():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiMdm()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_sender
            global t_msisdn
            global t_message
            global t_responetrxid
            global t_header_content_type
            global t_header_auth

            parsed_header_data = json.loads(json_data['header'])
            t_header_content_type = parsed_header_data.get('Content-Type')
            t_header_auth = parsed_header_data.get('Authorization')

            t_sender= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['sender'][0])
            t_msisdn= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['msisdn'][0])
            t_message= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['message'][0])
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiMdm():
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


def CheckVallueHeaderContentTypeMdmedia():
    std_content_type = 'application/x-www-form-urlencoded; charset=utf-8'
    str1 = "Content Type Standard ",std_content_type
    str2 = "Content Type In Header Dummy Result API = ", t_header_content_type
    result = Transmitter.MetchingData(std_content_type,  t_header_content_type, str1, str2)
    return(result)

def CheckVallueHeaderAuthMdmedia():
    str1 = "Auth From DB Config"
    str2 = "Auth From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username == ''):
            username = Transmitter.cfg_uid
        else:
            username = Transmitter.sid_queue_username
        if(Transmitter.sid_queue_password == ''):
            password = Transmitter.cfg_pwd
        else:
            password = Transmitter.sid_queue_password
        credentials = f"{username}:{password}"
    else:
        if(Transmitter.quinuid == ''):
            username = Transmitter.cfg_uid
        else:
            username = Transmitter.quinuid
        if(Transmitter.quinpwd == ''):
            password = Transmitter.cfg_pwd
        else:
            password = Transmitter.quinpwd
        credentials = f"{username}:{password}"
    Auth = base64.b64encode(credentials.encode()).decode()
    Auth = f'Basic {Auth}'
    result = Transmitter.MetchingData(Auth, t_header_auth, str1, str2)
    return (result)


def CheckValueSenderMdmedia():
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
    str1 = "sender From Queue =",c_sid
    str2 = "sender From Queue / Table  =",t_sender
    result = Transmitter.MetchingData(c_sid, t_sender, str1, str2)
    return(result)


def CheckValueMsisdnMdmedia():
	str1 = "msisdn From Queue =",Transmitter.quinmsisdn
	str2 = "msisdn From Queue / Table  =",t_msisdn
	result = Transmitter.MetchingData(Transmitter.quinmsisdn,t_msisdn, str1, str2)
	return(result)


def CheckValueMessageMdmedia():
	str1 = "message From Queue =",Transmitter.quinmessage
	str2 = "message From Queue / Table  =",urllib.parse.unquote_plus(t_message)
	result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quinmessage),t_message, str1, str2)
	return(result)