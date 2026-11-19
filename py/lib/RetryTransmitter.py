from datetime import datetime, timedelta
import sys,os,json,time,re
from pymongo import MongoClient

_curr_dir = os.path.dirname(os.path.abspath(__file__))
_py_dir = os.path.abspath(os.path.join(_curr_dir, ".."))
_conf_dir = os.path.join(_py_dir, "conf")
_mongo_dir = os.path.join(_curr_dir, "mongodb")

for p in (_py_dir, _conf_dir, _mongo_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

import Transmitter
from config import *
from MongoJNS import *
mg = mongo()

def SetVariableRetryTransmitterMongoDB():
    result_Db = mg.GetRetryTransmitter(str(Transmitter.quintrxid))
    if (result_Db is None):
        result = {
            "status": "NOK",
            "message": "Tidak Put Queue Retry Transmitter"
        }
    else:

        global r_transmitter_mongo
        global r_transmitter_mongo_next_schedule
        global r_transmitter_mongo_created_at
        global effective_site_mode

        created_at_values = result_Db['created_at']
        next_schedule_values = result_Db['next_schedule']

        # Tambahkan 7 jam ke setiap nilai
        result_Db['created_at'] = created_at_values + timedelta(hours=7)
        result_Db['next_schedule'] = next_schedule_values + timedelta(hours=7) - timedelta(seconds=int(Transmitter.cfg_retry_schedule_time))

        # Ubah format menjadi string jika diperlukan
        result_Db['created_at'] = result_Db['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        result_Db['next_schedule'] = result_Db['next_schedule'].strftime('%Y-%m-%d %H:%M:%S')

        print(result_Db)

        json_dd = json.dumps(result_Db)
        data = json.loads(json_dd)
        if 'created_at' in data:
            r_transmitter_mongo_created_at = data['created_at']
            del data['created_at']
        if 'next_schedule' in data:
            r_transmitter_mongo_next_schedule = data['next_schedule']
            del data['next_schedule']
        
        # Determine effective site mode (configurable: 'auto' | 'dual_site' | 'one_site')
        configured_mode = getattr(Transmitter, 'site_mode', globals().get('site_mode', 'auto'))
        if configured_mode == 'auto':
            # Auto-detect: if document contains 'site', use dual_site; else legacy one_site
            effective_site_mode = 'dual_site' if 'site' in data else 'one_site'
        else:
            effective_site_mode = configured_mode

        print(f"[RetryTransmitter] Effective site mode: {effective_site_mode}")

        if effective_site_mode == 'one_site':
            # In one_site (legacy PROD) mode, strip dual-site fields so comparison matches legacy schema
            data.pop('site', None)
            data.pop('status', None)
            data.pop('message_id', None)

        r_transmitter_mongo = json.dumps(data)
        print(r_transmitter_mongo)
        GeneratedRetryTransmitter(effective_site_mode)
        result = {
            "status": "OK",
            "message": "OK"
        }
    return (result)

def GeneratedRetryTransmitter(current_mode='auto'):
    global gen_transmitter_mongo
    global gendatetime
    gentimestamp = str(int(time.time()))
    datetime_obj = datetime.fromtimestamp(int(gentimestamp))
    gendatetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    retry = str(int(Transmitter.quinretry) + 1)
    queueTransmiter = ProccesingQueue(Transmitter.queuemessage)
    
    gen_dict = {
        "trx_id" : str(Transmitter.quintrxid),
        "queue_message" : queueTransmiter,
        "queue_name_transmitter" : Transmitter.quinchannel_mq_name,
        "priority" : str(Transmitter.quinpriority),
        "retry" : retry
    }

    if current_mode == 'dual_site':
        # v1.3.0 Dual-Site Contract: includes site, status=READY, message_id
        expected_site = getattr(Transmitter, 'cfg_instance_site', None) or 'PROD'
        expected_message_id = getattr(Transmitter, 'quinmessageid', '')
        gen_dict["site"] = expected_site
        gen_dict["status"] = "READY"
        gen_dict["message_id"] = str(expected_message_id)

    gen_transmitter_mongo = json.dumps(gen_dict)
    print(gen_transmitter_mongo)   

def ProccesingQueue(query_string):
    match = re.search(r'&retry=(\d+)', query_string)
    if match:
        # Jika retry sudah ada, tambahkan nilai retry
        retry_value = int(match.group(1)) + 1
        query_string = re.sub(r'&retry=\d+', f'&retry={retry_value}', query_string)
    else:
        # Jika retry belum ada, tambahkan parameter retry dengan nilai 1
        query_string += '&retry=1'
    
    return query_string


def CheckJsonRetryTransmitterMongoDB():
    # print(Transmitter.gen_messageinpushhistory_mongo)
    json_data1 = json.loads(gen_transmitter_mongo)
    json_data2 = json.loads(r_transmitter_mongo)
    print(json_data1)
    print(json_data2)
    str1 = "Json Object From Genrated = ",json_data1
    str2 = "Json Object In MongoDB Collection MSgIn_PushHistory = ", json_data2
    result = Transmitter.MetchingData(json_data1,  json_data2, str1, str2)
    return(result)

def CheckJsonRetryTransmitterMongoDB_created_at():
    str1 = "Generated DateTime Now = ",gendatetime
    str2 = "Json Object In MongoDB Collection MSgIn_PushHistory DateSubmit= ", r_transmitter_mongo_created_at
    result = Transmitter.MatchingDataDateTime(gendatetime,  r_transmitter_mongo_created_at, str1, str2)
    print(result)
    return(result)    

def CheckJsonRetryTransmitterMongoDB_next_schedule():
    str1 = "Generated DateTime Now = ",gendatetime
    str2 = "Json Object In MongoDB Collection MSgIn_PushHistory DateSubmit= ", r_transmitter_mongo_next_schedule
    result = Transmitter.MatchingDataDateTime(gendatetime,  r_transmitter_mongo_next_schedule, str1, str2)
    print(result)
    return(result)

def CheckDualSiteDeduplicationMongoDB():
    """Validates that exactly 1 document exists in MongoDB retry_transmitter for the given trx_id.
    
    Proves that when both PROD (.51) and DRC (.58) receive identical queue messages,
    the Single DB unique index {trx_id, message_id} successfully deduplicates and prevents
    double storage.
    """
    client = MongoClient(mongo_conn)
    db = client['scheduler_retry']
    coll = db['retry_transmitter']
    
    trxid = str(Transmitter.quintrxid)
    msgid = str(Transmitter.quinmessageid)
    
    docs = list(coll.find({'trx_id': trxid}))
    doc_count = len(docs)
    print(f"[CheckDualSiteDeduplicationMongoDB] trx_id={trxid}, found {doc_count} documents in MongoDB")
    for d in docs:
        print(f" - Doc ID: {d.get('_id')}, trx_id: {d.get('trx_id')}, site: {d.get('site')}, status: {d.get('status')}, message_id: {d.get('message_id')}")
    
    client.close()
    
    if doc_count != 1:
        return {
            "status": "NOK",
            "message": f"Expected exactly 1 document in MongoDB for trx_id={trxid}, but found {doc_count} (Deduplication failed!)"
        }
    
    doc = docs[0]
    site = doc.get('site')
    status = doc.get('status')
    stored_msgid = doc.get('message_id')
    
    if site not in ('PROD', 'DRC'):
        return {
            "status": "NOK",
            "message": f"Document has invalid site={site}, expected PROD or DRC"
        }
    if status != 'READY':
        return {
            "status": "NOK",
            "message": f"Document has invalid status={status}, expected READY"
        }
    if msgid and stored_msgid != msgid:
        return {
            "status": "NOK",
            "message": f"Document message_id mismatch: expected={msgid}, actual={stored_msgid}"
        }
        
    return {
        "status": "OK",
        "message": f"Deduplication SUCCESS: exactly 1 document stored in MongoDB (site={site}, status={status}, message_id={stored_msgid})"
    }   