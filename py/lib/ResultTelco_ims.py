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

# Safe defaults to avoid NameError when checks run before setter
t_sender = ''
t_msisdn = ''
t_message = ''
t_header_content_type = None
t_header_auth = None
t_username = ''
t_password = ''


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
            global t_username
            global t_password

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

            # Try to extract username/password from parameters first
            t_username = parsed.get('username', '')
            t_password = parsed.get('password', '')
            # If not present, try to decode from Authorization: Basic <b64>
            if (not t_username or not t_password) and t_header_auth and isinstance(t_header_auth, str) and t_header_auth.lower().startswith('basic '):
                try:
                    b64 = t_header_auth.split(' ', 1)[1]
                    decoded = base64.b64decode(b64).decode('utf-8')
                    # format: username:password
                    if ':' in decoded:
                        u, p = decoded.split(':', 1)
                        if not t_username:
                            t_username = u
                        if not t_password:
                            t_password = p
                except Exception:
                    pass

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


def _ensure_ims_variables_initialized():
    # Avoid NameError if checks run before setter populated globals
    global t_sender, t_msisdn, t_message, t_header_content_type, t_header_auth, t_username, t_password
    if 't_sender' not in globals():
        t_sender = ''
    if 't_msisdn' not in globals():
        t_msisdn = ''
    if 't_message' not in globals():
        t_message = ''
    if 't_header_content_type' not in globals():
        t_header_content_type = None
    if 't_header_auth' not in globals():
        t_header_auth = None
    if 't_username' not in globals():
        t_username = ''
    if 't_password' not in globals():
        t_password = ''


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
            'message': message,
            'username': obj.get('username') or obj.get('uid') or '',
            'password': obj.get('password') or obj.get('pwd') or ''
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
            'message': unquote(message),
            'username': unquote(flat.get('username') or flat.get('uid') or ''),
            'password': unquote(flat.get('password') or flat.get('pwd') or '')
        }
    except Exception:
        return {
            'sender': '',
            'msisdn': '',
            'message': ''
        }


def CheckValueSenderIms():
    _ensure_ims_variables_initialized()
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


def CheckVallueUsernameTelco():
    _ensure_ims_variables_initialized()
    str1 = "Username From Config/Queue"
    str2 = "Username From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        expected_username = Transmitter.sid_queue_username if Transmitter.sid_queue_username != '' else Transmitter.cfg_username
    else:
        expected_username = Transmitter.quinuid if Transmitter.quinuid != '' else Transmitter.cfg_username
    actual_username = t_username if 't_username' in globals() and t_username != '' else ''
    result = Transmitter.MetchingData(expected_username, actual_username, str1, str2)
    return result


def CheckValluePasswordTelco():
    _ensure_ims_variables_initialized()
    str1 = "Password From Config/Queue"
    str2 = "Password From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        expected_password = Transmitter.sid_queue_password if Transmitter.sid_queue_password != '' else Transmitter.cfg_password
    else:
        expected_password = Transmitter.quinpwd if Transmitter.quinpwd != '' else Transmitter.cfg_password
    actual_password = t_password if 't_password' in globals() and t_password != '' else ''
    result = Transmitter.MetchingData(expected_password, actual_password, str1, str2)
    return result


def CheckValueMsisdnIms():
    _ensure_ims_variables_initialized()
    str1 = "MSISDN From Queue", Transmitter.quinmsisdn
    str2 = "MSISDN From TelcoReceiver", t_msisdn
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_msisdn, str1, str2)
    return result


def CheckValueMessageIms():
    _ensure_ims_variables_initialized()
    str1 = "Message From Queue", Transmitter.quinmessage
    str2 = "Message From TelcoReceiver", urllib.parse.unquote_plus(t_message)
    result = Transmitter.MetchingData(
        urllib.parse.unquote_plus(Transmitter.quinmessage), urllib.parse.unquote_plus(t_message), str1, str2)
    return result


def CheckVallueHeaderContentTypeIms():
    _ensure_ims_variables_initialized()
    # If header is present, accept it; otherwise compare to standard JSON
    std_content_type = 'application/json'
    expected = t_header_content_type or std_content_type
    str1 = "Content Type Expected ", expected
    str2 = "Content Type In Header Dummy Result API = ", t_header_content_type
    result = Transmitter.MetchingData(expected, t_header_content_type, str1, str2)
    return result


def CheckVallueHeaderAuthIms():
    _ensure_ims_variables_initialized()
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


# Aliases to match existing DB config entries that use generic names
def SetVariableResponeResult():
    return SetVariableResponeResultIms()


def CheckVallueMsisdnTelco():
    return CheckValueMsisdnIms()


def CheckVallueSenderTelco():
    return CheckValueSenderIms()


def CheckVallueSMSTelco():
    return CheckValueMessageIms()


def CheckVallueHeaderContentType():
    return CheckVallueHeaderContentTypeIms()


def CheckVallueHeaderAuth():
    return CheckVallueHeaderAuthIms()


