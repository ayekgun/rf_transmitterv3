import os
import sys
import Transmitter
import requests
import json
import urllib
import time
from datetime import datetime, timedelta
import base64

sys.path.append(os.path.abspath("py/conf"))
from config import *

sys.path.append(os.path.abspath("py/lib/mongodb"))
from MongoJNS import *
mg = mongo()


def SetVariableResponeResultPintar():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiPintar()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:

            global t_senderid
            global t_type
            global t_msisdn
            global t_message
            global t_username
            global t_password
            global t_token
            global t_callbackurl
            global t_callbackmethod
            global t_encoding


            json_load = json.loads(json_data['parameter'])
            t_senderid       = json_load ['senderid']
            t_type           = json_load ['type']
            t_msisdn         = json_load ['msisdn']
            t_encoding       = json_load ['encoding']
            t_message        = json_load ['message']
            t_username       = json_load ['username']
            t_password       = json_load ['password']
            t_token          = json_load ['token']
            t_callbackurl    = json_load ['callbackurl']
            t_callbackmethod = json_load ['callbackmethod']


            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiPintar():
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
def CheckCallbackMethodFromTelco():
    str1 = "Callback Method From Config"
    str2 = "Callback Method From TelcoReceiver"
    expected_callbackmethod = Transmitter.cfg_callback_method
    result = Transmitter.MetchingData(expected_callbackmethod, t_callbackmethod, str1, str2)
    return result

def CheckCallbackUrlFromTelco():
    str1 = "Callback URL From Config"
    str2 = "Callback URL From TelcoReceiver"
    expected_url = Transmitter.cfg_callback_url
    result = Transmitter.MetchingData(expected_url, t_callbackurl, str1, str2)
    return result

def CheckEncodingFromTelco():
    str1 = "Encoding From Config"
    str2 = "Encoding From TelcoReceiver"
    expected_encoding = Transmitter.cfg_encoding
    result = Transmitter.MetchingData(expected_encoding, t_encoding, str1, str2)
    return result

def CheckMessageContentFromTelco():
    str1 = "Message Content From Queue"
    str2 = "Message Content From TelcoReceiver"
    expected_message = urllib.parse.unquote_plus(Transmitter.quinmessage)
    telco_message = urllib.parse.unquote_plus(t_message)
    result = Transmitter.MetchingData(expected_message, telco_message, str1, str2)
    return result

def CheckMsisdnFromTelco():
    str1 = "MSISDN From Queue"
    str2 = "MSISDN From TelcoReceiver"
    expected_msisdn = Transmitter.quinmsisdn
    result = Transmitter.MetchingData(expected_msisdn, t_msisdn, str1, str2)
    return result

def CheckPasswordFromTelco():
    str1 = "Password From Config"
    str2 = "Password From TelcoReceiver"
    if Transmitter.senderids_support == 'true':
        expected_password = Transmitter.sid_queue_password or Transmitter.cfg_password
    else:
        expected_password = Transmitter.quinpwd or Transmitter.cfg_password
    result = Transmitter.MetchingData(expected_password, t_password, str1, str2)
    return result

def CheckSenderIdFromTelco():
    str1 = "Sender ID From Queue"
    str2 = "Sender ID From TelcoReceiver"
    if Transmitter.senderids_support == 'true':
        expected_senderid = Transmitter.sid_queue_senderid or ''
    else:
        expected_senderid = Transmitter.quinsenderid or ''
    result = Transmitter.MetchingData(expected_senderid, t_senderid, str1, str2)
    return result

def CheckTokenFromTelco():
    str1 = "Token From Config"
    str2 = "Token From TelcoReceiver"
    if Transmitter.senderids_support == 'true':
        expected_token = Transmitter.sid_queue_cpname if Transmitter.sid_queue_cpname else Transmitter.cfg_provider_token
    else:
        expected_token = Transmitter.quincpName if Transmitter.quincpName else  Transmitter.cfg_provider_token
    result = Transmitter.MetchingData(expected_token, t_token, str1, str2)
    return result

def CheckTypeFromTelco():
    str1 = "Message Type From Queue"
    str2 = "Message Type From TelcoReceiver"
    expected_type = "sms"
    result = Transmitter.MetchingData(expected_type, t_type, str1, str2)
    return result

def CheckUsernameFromTelco():
    str1 = "Username From Config"
    str2 = "Username From TelcoReceiver"
    if Transmitter.senderids_support == 'true':
        expected_username = Transmitter.sid_queue_username or Transmitter.cfg_username
    else:
        expected_username = Transmitter.quinuid or Transmitter.cfg_username
    result = Transmitter.MetchingData(expected_username, t_username, str1, str2)
    return result

def CheckDataTempForReroute():
    if Transmitter.flow_transmitter_status == 'valid' and int(Transmitter.dummy_respon) < 100:
        result_Db = mg.GetMongoPintarReroute(str(Transmitter.quinmessageid))
        print(Transmitter.quinmessageid)
        if (result_Db is None):
            result = {
                "status": "NOK",
                "message": "Tidak Insert Data Mongo Reroute Transmitter"
            }
        else:

            # global r_transmitter_mongo
            # global r_transmitter_mongo_next_schedule
            # global r_transmitter_mongo_created_at

            created_at_values = result_Db['created_at']
            updated_at_values = result_Db['updated_at']

            # Tambahkan 7 jam ke setiap nilai
            result_Db['created_at'] = created_at_values + timedelta(hours=7)
            result_Db['updated_at'] = updated_at_values + timedelta(hours=7)

            # Ubah format menjadi string jika diperlukan
            result_Db['created_at'] = result_Db['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            result_Db['updated_at'] = result_Db['updated_at'].strftime('%Y-%m-%d %H:%M:%S')

            # print(result_Db)

            json_dd = json.dumps(result_Db)
            data = json.loads(json_dd)
            if 'created_at' in data:
                r_transmitter_mongo_created_at = data['created_at']
                del data['created_at']
            if 'updated_at' in data:
                r_transmitter_mongo_created_at = data['updated_at']
                del data['updated_at']
            
            r_datamongo_reroute = data    
            ExpectedRerouteMongo = GeneratedRerouteTransmitter()
            print(ExpectedRerouteMongo)
            print(r_datamongo_reroute)
            str1 = "MongoDB Expected = ",ExpectedRerouteMongo
            str2 = "MongoDB Actual = ", r_datamongo_reroute
            result = Transmitter.MetchingData(ExpectedRerouteMongo,  r_datamongo_reroute, str1, str2)
            return(result)
    else:
        result_Db = mg.GetMongoPintarReroute(str(Transmitter.quinmessageid))
        print(Transmitter.quinmessageid)
        if (result_Db is None):
            result = {
            "status": "OK",
            "message": "Transaksi Tidak Valid , Tidak Insert Queue Reroute Transmitter"
        }
        else:
            result = {
                "status": "NOK",
                "message": "Transaksi Tidak Valid , Tetapi Tetap Insert Queue Reroute Transmitter"
            }
    return (result)

def GeneratedRerouteTransmitter():
    queueTransmiter = Transmitter.queuemessage    
    gen_datareroute_mongo = {
            "trx_id" : str(Transmitter.quinmessageid),
            "provider_trx_id" : str(Transmitter.generatediddash),
            "job_id" : str(Transmitter.quintrxid),
            "queue_message" : queueTransmiter
        }
    # gen_datareroute_mongo = json.loads(gen_datareroute_mongo) 
    
    # print(gen_datareroute_mongo)  
    return (gen_datareroute_mongo)

# def CheckRetryHitIfStatusError():
#     str1 = "Retry Count via API"
#     str2 = "Retry Count in Config"

#     retry_exception_list = [x.strip() for x in Transmitter.cfg_retry_exception.split(',')]

#     if (
#         Transmitter.cfg_max_retry > 1
#         and Transmitter.dummy_status == "FAILED"
#         and Transmitter.dummy_httpcode not in retry_exception_list
#     ):
#         try:
#             url = f"http://192.168.181.52:8071/api_selenium/index.php/CekResult?id={Transmitter.generatediddash}"
#             response = requests.get(url)
#             response.raise_for_status()
#             json_data = response.json()

#             if isinstance(json_data, list):
#                 jumlah_retry = len(json_data)
#             else:
#                 jumlah_retry = 1  # fallback kalau hanya 1 object dikembalikan

#             retry_config = Transmitter.cfg_max_retry + 1  # +1 untuk hit awal

#             result = Transmitter.MetchingData(jumlah_retry,   Transmitter.cfg_max_retry, str1, str2)

#         except Exception as e:
#             result = {
#                 "status": "ERROR",
#                 "message": f"Gagal call API atau parsing JSON: {str(e)}"
#             }
#     else:
#         result = {
#             "status": "OK",
#             "message": "Tidak masuk syarat untuk cek retry hit via API"
#         }

#     return result



#end check hit Telco
