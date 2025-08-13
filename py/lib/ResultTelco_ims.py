import os
import sys
import Transmitter
import requests
import json
import urllib
import time
import base64

from urllib.parse import parse_qs, unquote

sys.path.append(os.path.abspath("py/conf"))
from config import *


def SetVariableResponeResultIms():
    if (Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiIms()
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

            # Header optional, depends on provider dummy
            try:
                parsed_header_data = json.loads(json_data.get('header', '{}'))
            except Exception:
                parsed_header_data = {}

            t_header_content_type = parsed_header_data.get('Content-Type')
            t_header_auth = parsed_header_data.get('Authorization')

            param = json_data.get('parameter', '')
            parsed = _parse_generic_params(param)

            t_sender = parsed.get('sender', '')
            t_msisdn = parsed.get('msisdn', '')
            t_message = parsed.get('message', '')
            t_responetrxid = json_data.get('respon')

            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiIms():
    n = 1
    while n <= 3:
        url = urlcekresult + str(Transmitter.generatediddash)
        req = requests.get(url)
        json_data = json.loads(req.text)
        n += 1
        if (json_data == 'Data Not Found'):
            print(url)
            result = json_data
            time.sleep(2)
        else:
            result = json_data
            break

    print(result)
    return result


def _parse_generic_params(parameter_str: str) -> dict:
    # Try JSON first (e.g., Infobip-like payload)
    try:
        obj = json.loads(parameter_str)
        # Infobip-like
        if isinstance(obj, dict) and 'messages' in obj:
            messages = obj.get('messages', [])
            if messages:
                msg0 = messages[0]
                sender = msg0.get('from', '')
                # destinations can be list of dicts with key 'to'
                to_val = ''
                try:
                    to_val = msg0.get('destinations', [{}])[0].get('to', '')
                except Exception:
                    to_val = ''
                text = msg0.get('text', '')
                return {
                    'sender': sender,
                    'msisdn': to_val,
                    'message': text
                }
        # Generic JSON flat
        sender = obj.get('sender') or obj.get('from') or ''
        msisdn = obj.get('msisdn') or obj.get('recipient') or obj.get('to') or ''
        message = obj.get('message') or obj.get('text') or obj.get('content') or ''
        return {
            'sender': sender,
            'msisdn': msisdn,
            'message': message
        }
    except Exception:
        pass

    # Fallback: URL-encoded query string (e.g., XL/Mdmedia/SOIP-like)
    try:
        q = parse_qs(parameter_str, keep_blank_values=True)
        # Flatten single-value lists and URL-decode
        flat = {k: (v[0] if isinstance(v, list) and len(v) > 0 else '') for k, v in q.items()}
        sender = flat.get('sender') or flat.get('from') or flat.get('senderid') or ''
        msisdn = flat.get('msisdn') or flat.get('recipient') or flat.get('to') or flat.get('phones') or ''
        message = flat.get('message') or flat.get('text') or flat.get('content') or ''
        return {
            'sender': unquote(sender),
            'msisdn': unquote(msisdn),
            'message': unquote(message)
        }
    except Exception:
        return {
            'sender': '',
            'msisdn': '',
            'message': ''
        }


def CheckValueSenderIms():
    if (Transmitter.senderids_support == 'true'):
        if (Transmitter.sid_queue_senderid != ''):
            c_sid = Transmitter.sid_queue_senderid
        else:
            c_sid = ''
    else:
        if (Transmitter.quinsenderid != ''):
            c_sid = Transmitter.quinsenderid
        else:
            c_sid = ''
    str1 = "Sender From Queue", c_sid
    str2 = "Sender From TelcoReceiver", t_sender
    result = Transmitter.MetchingData(c_sid, t_sender, str1, str2)
    return result


def CheckValueMsisdnIms():
    str1 = "MSISDN From Queue", Transmitter.quinmsisdn
    str2 = "MSISDN From TelcoReceiver", t_msisdn
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return result


def CheckValueMessageIms():
    str1 = "Message From Queue", Transmitter.quinmessage
    str2 = "Message From TelcoReceiver", urllib.parse.unquote_plus(t_message)
    result = Transmitter.MetchingData(
        urllib.parse.unquote_plus(Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return result


def CheckVallueHeaderContentTypeIms():
    # If header is present, accept it; otherwise compare to standard JSON
    std_content_type = 'application/json'
    expected = t_header_content_type or std_content_type
    str1 = "Content Type Expected ", expected
    str2 = "Content Type In Header Dummy Result API = ", t_header_content_type
    result = Transmitter.MetchingData(expected, t_header_content_type, str1, str2)
    return result


def CheckVallueHeaderAuthIms():
    str1 = "Auth From DB/Queue"
    str2 = "Auth From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if (Transmitter.sid_queue_username == ''):
            username = Transmitter.cfg_username
        else:
            username = Transmitter.sid_queue_username
        if (Transmitter.sid_queue_password == ''):
            password = Transmitter.cfg_password
        else:
            password = Transmitter.sid_queue_password
    else:
        if (Transmitter.quinuid == ''):
            username = Transmitter.cfg_username
        else:
            username = Transmitter.quinuid
        if (Transmitter.quinpwd == ''):
            password = Transmitter.cfg_password
        else:
            password = Transmitter.quinpwd
    credentials = f"{username}:{password}"
    auth = base64.b64encode(credentials.encode()).decode()
    auth = f'Basic {auth}'
    result = Transmitter.MetchingData(auth, t_header_auth, str1, str2)
    return result


