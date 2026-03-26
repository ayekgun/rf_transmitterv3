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
    # Initialize globals to prevent NameError in subsequent checks even if this one fails
    global t_appsid, t_msisdn, t_pwd, t_sid, t_sms, t_responetrxid
    t_appsid = t_msisdn = t_pwd = t_sid = t_sms = t_responetrxid = ''
    
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
            # TelkomselHttpHandlerImpl.java only sends 6 parameters: appsid, pwd, sid, trx_id, msisdn, sms
            params = urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)
            
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
    # Formats to try:
    # 1. jts-<uuid-no-dash> (legacy format)
    # 2. <uuid-no-dash>
    # 3. jts-<uuid-with-dash>
    # 4. <uuid-with-dash> (original messageid)
    
    raw_uuid = str(Transmitter.generatediddash)
    nodash_uuid = raw_uuid.replace('-', '')
    
    formats = [
        'jts-' + nodash_uuid,
        nodash_uuid,
        'jts-' + raw_uuid,
        raw_uuid
    ]
    
    while n <= 3:
        for fmt in formats:
            url = urlcekresult + fmt
            try:
                req = requests.get(url)
                if req.status_code == 200:
                    json_data = json.loads(req.text)
                    if json_data != 'Data Not Found':
                        print(f"[DEBUG] Found hit telco with ID: {fmt}")
                        return json_data
            except Exception as e:
                print(f"[DEBUG] Error hitting dummy API: {str(e)}")
        
        print(f"[DEBUG] Retry {n}/3: Data Telco not found yet for any fallback ID format.")
        n += 1
        time.sleep(2)

    return 'Data Not Found'

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
    str1 = "Message From Queue"
    str2 = "Message From TelcoReceiver"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(
        Transmitter.quinmessage), urllib.parse.unquote_plus(t_sms), str1, str2)
    return (result)

# Aliases for compatibility with Tsel/General keywords in DB
SetVariableResponeResultTsel = SetVariableResponeResultTelkomsel
CheckVallueAppidTelco = CheckVallueAppidTelkomsel
CheckVallueMsisdnTelco = CheckVallueMsisdnTelkomsel
CheckValluePwdTelco = CheckValluePwdTelkomsel
CheckVallueSidTelco = CheckVallueSidTelkomsel
CheckVallueSMSTelco = CheckVallueSMSTelkomsel

# Note: cp_name and trx_date checks removed as they are not sent by TelkomselHttpHandlerImpl.java

#end check hit Telco
