from datetime import datetime, timedelta
import sys,os,json,time,re

sys.path.append(os.path.abspath("py"))
import Transmitter

sys.path.append(os.path.abspath("py/conf"))
from config import *

sys.path.append(os.path.abspath("py/lib/mongodb"))
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
        
        r_transmitter_mongo = json.dumps(data)
        print(r_transmitter_mongo)
        GeneratedRetryTransmitter()
        result = {
            "status": "OK",
            "message": "OK"
        }
    return (result)

def GeneratedRetryTransmitter():
    global gen_transmitter_mongo
    global gendatetime
    gentimestamp = str(int(time.time()))
    datetime_obj = datetime.fromtimestamp(int(gentimestamp))
    gendatetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    retry = str(int(Transmitter.quinretry) + 1)
    queueTransmiter = ProccesingQueue(Transmitter.queuemessage)
    
    gen_transmitter_mongo = {
            "trx_id" : str(Transmitter.quintrxid),
            "queue_message" : queueTransmiter,
            "queue_name_transmitter" : Transmitter.quinchannel_mq_name ,
            "priority" : str(Transmitter.quinpriority),
            "retry" : retry
        }
    gen_transmitter_mongo = json.dumps(gen_transmitter_mongo)
    
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