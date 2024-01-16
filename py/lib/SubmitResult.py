import pymysql
import re
import sys
import os
import time
from datetime import datetime, timedelta

sys.path.append(os.path.abspath("py"))
import Transmitter

sys.path.append(os.path.abspath("py/lib"))
from TelcoFunction import *

sys.path.append(os.path.abspath("py/conf"))
from config import *

def GetDataQueueSubmitResult():
    n = 1
    while n <= 3:
        con = pymysql.connect(db=db, user=user, passwd=passwd,
                              host=host, port=3306, autocommit=False)
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM out_submitresult where  trxid = %s", (Transmitter.quinmessageid,))
        resultDB = cur.fetchone()
        n += 1
        if (resultDB is None):
            print(n)
            cur.close()
            time.sleep(1)
        else:
            break
            cur.close()

    return (resultDB)

def SetVariableQueueSubmitResult():
    result_Db = GetDataQueueSubmitResult()
    if (result_Db is None):
        result = {
            "status": "NOK",
            "message": "Data Transaction tidak ada / Tidak Put Queue Submit Result"
        }
    else:
        i = 0
        while i < len(dic_queuesm):
            globals()['qsm_'+dic_queuesm[i]] = result_Db[i]
            i += 1
        result = {
            "status": "OK",
            "message": "OK"
        }
        SetVaribaleResponeDummy()
    # print(qsm_channel_name)
    return (result)

def SetVaribaleResponeDummy():
    global respone_pss
    global respone_tss
    con = pymysql.connect(db=db, user=user, passwd=passwd,
                          host=host, port=3306, autocommit=False)
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM dummy_respon where provider = %s  and `default` = %s ", (Transmitter.provider, '1'))
    resultDB = cur.fetchone()
    respone_pss = resultDB[9]
    respone_tss = resultDB[10]
    return(resultDB)

def CheckVallueSubmitResultChannelName():
    provider_name = Transmitter.GetProvider(Transmitter.quinproviderid)
    str1 = "Channel Name Queue IN"
    str2 = "ChannelName Queue Submit Result"
    result = Transmitter.MetchingData(provider_name, qsm_channel_name, str1, str2)
    return (result)


def CheckVallueSubmitResultProviderSubmitStatus():
    str1 = "Provider Submit Status in Config Dummy status"
    str2 = "Provider Submit Status in Queue Submit Result"
    if(Transmitter.CheckFlowToTelco() == 'expired'):
        c_submitstatus = Transmitter.cfg_ERR_EXPIRED
    else:
        c_submitstatus = respone_pss
    result = Transmitter.MetchingData(
        c_submitstatus, qsm_provider_submit_status, str1, str2)
    return (result)


def CheckVallueSubmitResultDateHit():
    str1 = "Provider Submit Status in Config Dummy status"
    str2 = "Provider Submit Status in Queue Submit Result"
    result = Transmitter.MetchingData(1, 1, str1, str2)
    return (result)


def CheckVallueSubmitResultTransmitterSubmitStatus():
    str1 = "Transmitter Submit Status in Config Dummy status"
    str2 = "Transmitter Submit Status in Queue Submit Result"
    if(Transmitter.CheckFlowToTelco() == 'expired'):
        c_submitstatus = Transmitter.cfg_FAILED_SUBMIT
    else:
        c_submitstatus = respone_tss
    result = Transmitter.MetchingData(
        c_submitstatus, qsm_transmitter_submit_status, str1, str2)
    return (result)


def CheckVallueSubmitResultDateResponse():
    str1 = "Provider Submit Status in Config Dummy status"
    str2 = "Provider Submit Status in Queue Submit Result"
    result = Transmitter.MetchingData(1, 1, str1, str2)
    return (result)


def CheckVallueSubmitResultDivisionId():
    str1 = "Division ID Queue IN"
    str2 = "Division ID Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quindivisionid, qsm_division_id, str1, str2)
    return (result)


def CheckVallueSubmitResultChargecode():
    str1 = "Chargecode Queue IN"
    str2 = "Chargecode Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quinchargecode, qsm_chargecode, str1, str2)
    return (result)


def CheckVallueSubmitResultTrxid():
    str1 = "TRX ID Queue IN"
    str2 = "TRX ID Queue Submit Result"
    result = Transmitter.MetchingData(str(Transmitter.generatediddash), qsm_trxid, str1, str2)
    return (result)


def CheckVallueSubmitResultClientId():
    str1 = "Client ID Queue IN"
    str2 = "Client ID Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quinclientid, qsm_client_id, str1, str2)
    return (result)


def CheckVallueSubmitResultChannelMqName():
    str1 = "Client ID Queue IN"
    str2 = "Client ID Queue Submit Result"
    if(Transmitter.quinoriginmqname == ''):
        c_mqname = Transmitter.cfg_activemq_txque
    elif(Transmitter.quinoriginmqname == Transmitter.queue818):
        c_mqname = Transmitter.quinoriginmqname
    elif(Transmitter.quinoriginmqname == Transmitter.queue623):
        c_mqname = Transmitter.quinoriginmqname
    elif(Transmitter.quinoriginmqname == Transmitter.queue247):
        c_mqname = Transmitter.quinoriginmqname
    else:
        c_mqname = Transmitter.cfg_activemq_txque
    result = Transmitter.MetchingData(c_mqname, qsm_channel_mq_name, str1, str2)
    return (result)


def CheckVallueSubmitResultChannelIsDirect():
    str1 = "Client ID Queue IN"
    str2 = "Client ID Queue Submit Result"
    if (Transmitter.senderids_support == 'true'):
        c_channelisdirect = str(Transmitter.sid_queue_isdirect)
    else:
        c_channelisdirect = ''
    result = Transmitter.MetchingData(c_channelisdirect, qsm_channel_is_direct, str1, str2)
    return (result)


def CheckVallueSubmitResultDuration():
    str1 = "Duration"
    str2 = "Duration"
    result = Transmitter.MetchingData(1, 1, str1, str2)
    return (result)


def CheckVallueSubmitResultServiceType():
    str1 = "Service Type Queue IN"
    str2 = "Service Type Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quinservicetype, qsm_service_type, str1, str2)
    return (result)


def CheckVallueSubmitResultWithoutDr():
    if(Transmitter.cfg_provider_hasdr == 'true'):
        without_dr = 'false'
    else:
        without_dr = 'true'
    str1 = "Without DR Config Transmitter"
    str2 = "Without DR Queue Submit Result"
    result = Transmitter.MetchingData(without_dr, qsm_without_dr, str1, str2)
    return (result)


def CheckVallueSubmitResultJobId():
    str1 = "Job ID Queue In"
    str2 = "Job ID Queue Submit Result"
    result = Transmitter.MetchingData(
        Transmitter.generatedid, qsm_job_id, str1, str2)
    return (result)


def CheckVallueSubmitResultMaskName():
    str1 = "Mask Name Queue IN"
    str2 = "Mask Name Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quinsender, qsm_mask_name, str1, str2)
    return (result)


def CheckVallueSubmitResultProviderId():
    str1 = "Provider ID Queue IN"
    str2 = "Provider ID Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quinproviderid, qsm_provider_id, str1, str2)
    return (result)

def CheckVallueSubmitResultProviderName():
    str1 = "Provider Name Queue IN"
    str2 = "Provider Name Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.cfg_channel_name, qsm_provider_name, str1, str2)
    return (result)


def CheckVallueSubmitResultMaskId():
    str1 = "MaskId"
    str2 = "MaskId"
    result = Transmitter.MetchingData("", qsm_mask_id, str1, str2)
    return (result)


def CheckVallueSubmitResultMessageSeq():
    str1 = "Message Sequence Queue IN"
    str2 = "Message Sequence Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.quinsmspartition, qsm_message_seq, str1, str2)
    return (result)


def CheckVallueSubmitResultRetry():
    str1 = "Retry"
    str2 = "Retry"
    result = Transmitter.MetchingData(1, 1, str1, str2)
    return (result)


def CheckVallueSubmitResultPriorityHeader():
    str1 = "Priority Header Queue IN"
    str2 = "Priority Header Queue Submit Result"
    result = Transmitter.MetchingData('4', qsm_priority_header, str1, str2)
    return (result)


def CheckVallueSubmitResultPersistent():
    str1 = "Persistent Queue IN"
    str2 = "Persistent Queue Submit Result"
    result = Transmitter.MetchingData(Transmitter.cfg_queue_persistency, qsm_persistent, str1, str2)
    return (result)

# def CheckVallueSubmitResult():
