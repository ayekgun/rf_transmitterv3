import os
import shutil
import uuid
import requests
import pymysql
import json
import re
import math
import time
import urllib
import xml.etree.ElementTree as ET
import sys

from datetime import datetime, timedelta
from urllib import parse

sys.path.append(os.path.abspath("py/conf"))
from config import *
from conf_xl import *
from conf_tsel import *
from conf_nadynehttp import *
from conf_jantara import *
from conf_modifylong import *
from conf_mitracomm import *
from conf_soip import *
from conf_dws import *
from conf_infobip import * 
from conf_mdmedia import * 
from conf_mustika import * 
from conf_pintar import * 
from conf_m360 import * 

sys.path.append(os.path.abspath("py/lib"))
from py.lib.RetryTransmitter import *
from ActiveMQ import *

from ResultTelco_tsel import *
from ResultTelco_xl import *
from ResultTelco_nadynehttp import *
from ResultTelco_jantara import *
from ResultTelco_modifylong import *
from ResultTelco_mitracomm import *
from ResultTelco_soip import *
from ResultTelco_dws import *
from ResultTelco_infobip import *
from ResultTelco_mdmedia import *
from ResultTelco_mustika import *
from ResultTelco_pintar import *
from ResultTelco_m360 import *

from SmartBreak import *
from SubmitResult import *
from SleepMode import *

from TransmitterRedirect import *

def SetConfigDynamic(var):
    global urlchangerespon
    global cfg_name818
    global cfg_name623
    global cfg_name247
    global queue818
    global queue623
    global queue247
    global provider
    global robotname
    global d_provider
    global cfglookup
    global retry_mechanisme
    global reroute_mechanisme
    
    d_provider = var.lower()
    urlchangerespon = eval(str(d_provider+'_urlchangerespon'))
    cfg_name818 = eval(d_provider+'_cfg_name818')
    cfg_name623 = eval(d_provider+'_cfg_name623')
    cfg_name247 = eval(d_provider+'_cfg_name247')
    queue818 = eval(d_provider+'_queue818')
    queue623 = eval(d_provider+'_queue623')
    queue247 = eval(d_provider+'_queue247')
    provider = eval(d_provider+'_provider')
    robotname = eval(d_provider+'_robotname')
    cfglookup = eval(d_provider+'_cfglookup')
    retry_mechanisme = eval(d_provider+'_retry_mechanisme')
    reroute_mechanisme = eval(d_provider+'_reroute_mechanisme')

def SetVariableTestCase(type ,testcase):
    global queuemessage
    global generatedid
    global generatediddash
    # generatedid = message id 
    generatedid = uuid.uuid4().hex[:24].upper()
    # generatediddash = trxid yang benar
    generatediddash = uuid.uuid4()
    result_Db = GetTestCase(testcase)
    i = 0
    while i < len(dic_testcase):
        print(dic_testcase[i], '=', result_Db[i + 1])
        if (dic_testcase[i] == 'quintrxid' and result_Db[1+i] == 'autotrxid'):
            globals() [dic_testcase[i]] = generatedid
        elif(dic_testcase[i] == 'quinmessageid' and result_Db[1+i] == 'automessageid'):
            globals() [dic_testcase[i]] = str(generatediddash)
        elif(dic_testcase[i] == 'quinexpiry' and result_Db[1+i] == 'expired'):
            globals() [dic_testcase[i]] = Setdateexpired(-5)
        elif(dic_testcase[i] == 'quinexpiry' and result_Db[1+i] == 'valid'):
            globals() [dic_testcase[i]] = Setdateexpired(5)
        elif(dic_testcase[i] == 'quinoriginmqname' and result_Db[1+i] == 'automq818'):
            globals() [dic_testcase[i]] = queue818
        elif(dic_testcase[i] == 'quinoriginmqname' and result_Db[1+i] == 'automq623'):
            globals() [dic_testcase[i]] = queue623
        elif(dic_testcase[i] == 'quinoriginmqname' and result_Db[1+i] == 'automq247'):
            globals() [dic_testcase[i]] = queue247
        elif(dic_testcase[i] == 'quinsenderids'):
            rplc_senderids = result_Db[1+i].replace("CHGPROVIDER", provider)
            globals()[dic_testcase[i]] = urllib.parse.quote_plus(
                str(rplc_senderids))
        else:
            globals() [dic_testcase[i]] = urllib.parse.quote_plus(str(result_Db[1+i]))
       
        i += 1
    
    queuemessage = eval(result_Db[37])
    print (queuemessage)
    SetNameQueue(type)
    SetConfigLookupTransmitter()
    return (result_Db)

def SetNameQueue(type):
    global queuename
    global cfg_queue
    if (type  ==  'T818'):
        queuename = queue818
        cfg_queue = cfg_name818
    elif (type  ==  'T623'):
        queuename = queue623
        cfg_queue = cfg_name623
    else:
        queuename = queue247
        cfg_queue = cfg_name247


def SendMessageQueue(prefname):
    global  txprefname
    txprefname = prefname
    SendQueue(queuemessage, queuename, prefname)

def GetKeywordFromDB(keyword):
    con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
    cur = con.cursor()
    sql ="SELECT subkeyword FROM config_keyword where status = 1 and appname in(%s,%s) and keyword = %s order by step asc"
    query = cur.execute(sql, (global_name_of_robot,robotname, keyword))
    print(sql, (global_name_of_robot,robotname, keyword))
    resultDB = cur.fetchall()
    resultDB = [x[0] for x in resultDB]
    # print (resultDB)
    return resultDB


def GetTestCase(testcase):
    n = 1
    while n <= 3:
        con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM transmitter where testcase = %s",(testcase))
        resultDB = cur.fetchone()
        n +=1
        if (resultDB is None):
            print(n)
            cur.close()
            time.sleep(2)
        else:
            break
            cur.close()

    return (resultDB)

def ChangeDummyRespone(id):
    global dummy_sleep
    global dummy_httpcode
    global dummy_respone_provider
    global dummy_respon
    global dummy_status
    url = urlchangerespon + str(id) + str("&trxid=") + str(generatediddash)
    req = requests.get(url)
    dummy_sleep = json.loads(req.text)['sleep']
    dummy_httpcode = json.loads(req.text)['http_request']
    dummy_respon = json.loads(req.text)['respon']
    dummy_status = json.loads(req.text)['status']
    dummy_respone_provider = json.loads(
        req.text)['respone_provider_submit_status']
    print(url)
    return(req)

def ChangeDummyResponeSleepMode():
    global dummy_sleep
    global dummy_httpcode
    global dummy_respone_provider
    id = GetTestResponeDummy()
    id = id[0]
    url = urlchangerespon + str(id) + str("&trxid=") + str(generatediddash)
    req = requests.get(url)
    dummy_sleep = json.loads(req.text)['sleep']
    dummy_httpcode = json.loads(req.text)['http_request']
    dummy_respone_provider = json.loads(
        req.text)['respone_provider_submit_status']
    print(url)
    return(req)


def CheckFlowToTelco():
    global new_retry_status
    global flow_transmitter_status
    datenow = datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')
    if(quinexpiry == ''):
        if(int(cfg_timeout) < int(dummy_sleep)):
            status = 'bypass'
            new_retry_status = False
        elif(dummy_httpcode  !=  '200'):
            status = 'bypass'
            if(retry_mechanisme == True):
                new_retry_status = ParseStatusRetry()
            else:
                new_retry_status = False
        else:
            status = 'valid'
            new_retry_status = False

    elif(datenow < quinexpiry):
        if(int(cfg_timeout) < int(dummy_sleep)):
            status = 'bypass'
            new_retry_status = False
        elif(dummy_httpcode  !=  '200'):
            status = 'bypass'
            if(retry_mechanisme == True):
                new_retry_status = ParseStatusRetry()
            else:
                new_retry_status = False
        else:
            status = 'valid'
            new_retry_status = False
    else:
        status = 'expired'
        new_retry_status = False
    # print(status)
    flow_transmitter_status = status
    return(status)

def CheckFlowNewRetryMechanisme():
    return new_retry_status


def CheckFlowNewRerouteMechanisme():
    return reroute_mechanisme


def ParseStatusRetry():
    retry_exception = cfg_retry_exception.split(',')
    retry_service_type = cfg_retry_service_type.split(',')
    print(retry_exception)
    print(retry_service_type)
    print(dummy_httpcode)
    print(quinservicetype)
    
    if int(quinretry) < int(cfg_max_retry):
        print(int(quinretry))
        print(int(cfg_max_retry))
        for code in retry_exception:
            if str(dummy_httpcode) == code:
                for rst in retry_service_type:
                    if quinservicetype == rst:
                        return True
                break  # Break out of the loop if a match is found in retry_exception
    
    return False

def GetTestResponeDummy():
    print(provider)
    con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
    cur = con.cursor()
    cur.execute("SELECT id FROM dummy_respon where provider = %s",(provider,))
    result_set = cur.fetchall()
    array = list()
    for row in result_set:
        array.append(row[0])
    return(array)
    #print(array)

def GetDataQueueResultDummy(): #method biasa
    n = 1
    while n <= 3:
        con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM queue_sm where  provider_trxid = %s",('jts-'+str(generatediddash).replace('-','')))
        print('jts-'+str(generatediddash).replace('-',''))
        resultDB = cur.fetchone()
        n +=1
        if (resultDB is None):
            print(n)
            cur.close()
            time.sleep(1)
        else:
            break
            cur.close()
    return (resultDB)

def GetProvider(id): #method biasa
    n = 1
    while n <= 3:
        con = pymysql.connect(db=db_bc, user=user_bc, passwd=passwd_bc,host=host_bc,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM providers where  id = %s",(id))
        resultDB = cur.fetchone()
        n +=1
        if (resultDB is None):
            print(n)
            cur.close()
        else:
            break
            cur.close()
    return (resultDB[1])

def GetChannelisDirect(): #method biasa
    n = 1
    while n <= 3:
        con = pymysql.connect(db=db_bc, user=user_bc, passwd=passwd_bc,host=host_bc,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM channel_groups where  name = %s",(cfg_channel_name))
        resultDB = cur.fetchone()
        n +=1
        if (resultDB is None):
            print(n)
            cur.close()
        else:
            break
            cur.close()
    return (resultDB[3])

def SetConfigLookupTransmitter():
    # cfg_queue = cfg_name818
    con = pymysql.connect(db=db_cfg, user=user_cfg, passwd=passwd_cfg,host=host_cfg,port=3306,autocommit=False)
    cur = con.cursor()
    cur.execute(cfglookup, cfg_queue)
    for row in cur:
        globals() ['cfg_'+row[0]] = row[1]
        # print(row[0],'=',row[1])
    cur.close()

def SetSenderidsParameterForCheck():
    global senderids_support
    senderids_support = 'false'
    if (quinsenderids  != ''):
        try:
            d = json.loads(urllib.parse.unquote_plus(quinsenderids))
            n = 1
            while n <= len(d['maskCodeSettings']):
                if (provider == d['maskCodeSettings'][n-1]['key']):
                    global sid_queue_password
                    global sid_queue_username
                    global sid_queue_senderid
                    global sid_queue_cpname
                    global sid_queue_isdirect
                    sid_queue_password = d['maskCodeSettings'][n-1]['data']['password']
                    sid_queue_username = d['maskCodeSettings'][n-1]['data']['username']
                    sid_queue_senderid = d['maskCodeSettings'][n-1]['data']['senderID']
                    sid_queue_cpname = d['maskCodeSettings'][n-1]['data']['cpName']
                    sid_queue_isdirect = d['maskCodeSettings'][n-1]['data']['channelIsDirect']
                    senderids_support = 'true'
                n +=1
        except:
            print('Format Json Tidak Sesuai')
    else:
        print('Senderids Not Available')



def Setdateexpired(time):
    datetime_object = datetime.now()
    datetime_object += timedelta(minutes=(time))
    date = datetime.strftime(datetime_object,'%Y%m%d%H%M%S')
    return(date)

def RunAMQTransmitter(sleeptime):
    sleep_after = max(1000, int(cfg_sleep_after_send)) / 1000.0  # minimal 1 detik
    delay = int(sleeptime) * sleep_after
    GetQueueTransmitter(queue247, int(delay))

def RunAmqSubmitResultHandler(sleeptime):
    # time = int(sleeptime) * int(cfg_sleep_after_send) / 1000
    sleep_after = max(1000, int(cfg_sleep_after_send)) / 1000.0  # minimal 1 detik
    delay = int(sleeptime) * sleep_after
    if(d_provider == 'xl'):
        time2 = CheckStatusForSleepRetry()
        GetQueueSubmitResult(queuesubmitresult, int(delay)+int(time2))
    else:
        GetQueueSubmitResult(queuesubmitresult,delay)


def CheckStatusForSleepRetry():
    global retryable
    cfg_retryable_error.split('|')
    cfg_retryable_servicetype.split('|')
    if(dummy_respone_provider in cfg_retryable_error and quinservicetype in cfg_retryable_servicetype):
        x = int(cfg_RETRY_TIMEOUT) / 1000 * \
            int(cfg_max_retry) + int(cfg_max_retry)
        retryable = 'true'
    else:
        x = 0
        retryable = 'false'
    return x
    

def SendTopicReload():
    SendTopic()
    time.sleep(5)

def SetTopicSmartBreake(msg,direct):
    SendTopicSmartBreake(queue247,msg,direct)


def MetchingData(var1, var2, string1, string2):
    if (var1 == var2):
        status = 'OK'
        validation = string1, var1, " &", string2, var2, "= Match"
    else:
        status = 'NOK'
        validation = string1, var1, " &", string2, var2, "= No Match"
    data = {
        "status": status,
        "message": validation
    }
    return data

def MatchingDataDateTime(var1, var2, string1, string2):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    date1 = datetime.strptime(var1, datetime_format)
    date2 = datetime.strptime(var2, datetime_format)
    if (-10 <= (date1 - date2).total_seconds() <= 10):
        status = 'OK'
        validation = string1, var1, " &", string2, var2, "= Selisih "+ str((date1 - date2).total_seconds())  
    else:
        status = 'NOK'
        validation = string1, var1, " &", string2, var2, "= Selisih Over "+   str((date1 - date2).total_seconds())  
    data = {
        "status": status,
        "message": validation
    }
    return data


# if __name__ == '__main__':
#     SetVariableTestCase('T247', '[TransJNS-003]')
