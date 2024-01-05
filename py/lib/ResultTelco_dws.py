import os
import sys
import Transmitter
import requests
import json
import urllib
import time

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultDws():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiDws()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            global t_number
            global t_sender
            global t_message
            global t_max_parts
            global t_encoding
            global t_url
            
            t_number= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['number'][0])
            t_sender= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['sender'][0])
            t_message= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['message'][0])
            t_max_parts= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['max_parts'][0])
            t_encoding= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['encoding'][0])
            t_url= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['url'][0])
            t_responetrxid = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiDws():
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


def CheckValueNumber():
	str1 = "number From Queue =",Transmitter.quinmsisdn
	str2 = "number From Queue / Table  =",t_number
	result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_number, str1, str2)
	return(result)


def CheckValueSender():
	str1 = "sender From Queue =",Transmitter.quinsender
	str2 = "sender From Queue / Table  =",t_sender
	result = Transmitter.MetchingData(Transmitter.quinsender, t_sender, str1, str2)
	return(result)


def CheckValueMessage():
	str1 = "message From Queue =",urllib.parse.unquote_plus(Transmitter.quinmessage)
	str2 = "message From Queue / Table  =",urllib.parse.unquote_plus(t_message)
	result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quinmessage),t_message, str1, str2)
	return(result)


def CheckValueMax_Parts():
	str1 = "max_parts From Queue =",Transmitter.cfg_
	str2 = "max_parts From Queue / Table  =",Transmitter.quoutmax_parts
	result = Transmitter.MetchingData(Transmitter.quinmax_parts, Transmitter.quoutmax_parts, str1, str2)
	return(result)


def CheckValueEncoding():
	str1 = "encoding From Queue =",Transmitter.cfg_encoding
	str2 = "encoding From Queue / Table  =",t_encoding
	result = Transmitter.MetchingData(Transmitter.cfg_encoding, t_encoding, str1, str2)
	return(result)


def CheckValueUrl():
	str1 = "url From Queue =",Transmitter.cfg_callbackUrl
	str2 = "url From Queue / Table  =",t_url
	result = Transmitter.MetchingData(Transmitter.cfg_callbackUrl, t_url, str1, str2)
	return(result)

#end check hit Telco
