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

def _log_to_console(message):
    """Helper function to write to both stdout and stderr for console visibility"""
    sys.stdout.write(message)
    sys.stderr.write(message)
    sys.stdout.flush()
    sys.stderr.flush()

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
    if resultDB is None:
        cur.execute("SELECT * FROM dummy_respon where `default` = '1' ORDER BY date_update DESC LIMIT 1")
        resultDB = cur.fetchone()
    if resultDB:
        respone_pss = resultDB[9]
        respone_tss = resultDB[10]
    return(resultDB)

def CheckVallueSubmitResultChannelName():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultChannelName] Starting Channel Name validation...\n")
    _log_to_console(separator + "\n")
    
    provider_name = Transmitter.GetProvider(Transmitter.quinproviderid)
    str1 = "Channel Name Queue IN"
    str2 = "ChannelName Queue Submit Result"
    
    _log_to_console("  Channel Name Validation Results:\n")
    result = Transmitter.MetchingData(provider_name, qsm_channel_name, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Channel Name: Expected '{provider_name}' matches Actual '{qsm_channel_name}'\n")
    else:
        _log_to_console(f"    ✗ Channel Name: Expected '{provider_name}' does not match Actual '{qsm_channel_name}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultProviderSubmitStatus():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultProviderSubmitStatus] Starting Provider Submit Status validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Provider Submit Status in Config Dummy status"
    str2 = "Provider Submit Status in Queue Submit Result"
    if(Transmitter.CheckFlowToTelco() == 'expired'):
        c_submitstatus = Transmitter.cfg_ERR_EXPIRED
    else:
        c_submitstatus = respone_pss
    
    _log_to_console("  Provider Submit Status Validation Results:\n")
    result = Transmitter.MetchingData(
        c_submitstatus, qsm_provider_submit_status, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Provider Submit Status: Expected '{c_submitstatus}' matches Actual '{qsm_provider_submit_status}'\n")
    else:
        _log_to_console(f"    ✗ Provider Submit Status: Expected '{c_submitstatus}' does not match Actual '{qsm_provider_submit_status}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultDateHit():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultDateHit] Starting Date Hit validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Provider Submit Status in Config Dummy status"
    str2 = "Provider Submit Status in Queue Submit Result"
    
    _log_to_console("  Date Hit Validation Results:\n")
    result = Transmitter.MetchingData(1, 1, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Date Hit: Expected '1' matches Actual '1'\n")
    else:
        _log_to_console(f"    ✗ Date Hit: Expected '1' does not match Actual '1'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultTransmitterSubmitStatus():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultTransmitterSubmitStatus] Starting Transmitter Submit Status validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Transmitter Submit Status in Config Dummy status"
    str2 = "Transmitter Submit Status in Queue Submit Result"
    if(Transmitter.CheckFlowToTelco() == 'expired'):
        c_submitstatus = Transmitter.cfg_FAILED_SUBMIT
    else:
        c_submitstatus = respone_tss
    
    _log_to_console("  Transmitter Submit Status Validation Results:\n")
    result = Transmitter.MetchingData(
        c_submitstatus, qsm_transmitter_submit_status, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Transmitter Submit Status: Expected '{c_submitstatus}' matches Actual '{qsm_transmitter_submit_status}'\n")
    else:
        _log_to_console(f"    ✗ Transmitter Submit Status: Expected '{c_submitstatus}' does not match Actual '{qsm_transmitter_submit_status}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultDateResponse():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultDateResponse] Starting Date Response validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Provider Submit Status in Config Dummy status"
    str2 = "Provider Submit Status in Queue Submit Result"
    
    _log_to_console("  Date Response Validation Results:\n")
    result = Transmitter.MetchingData(1, 1, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Date Response: Expected '1' matches Actual '1'\n")
    else:
        _log_to_console(f"    ✗ Date Response: Expected '1' does not match Actual '1'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultDivisionId():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultDivisionId] Starting Division ID validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Division ID Queue IN"
    str2 = "Division ID Queue Submit Result"
    
    _log_to_console("  Division ID Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quindivisionid, qsm_division_id, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Division ID: Expected '{Transmitter.quindivisionid}' matches Actual '{qsm_division_id}'\n")
    else:
        _log_to_console(f"    ✗ Division ID: Expected '{Transmitter.quindivisionid}' does not match Actual '{qsm_division_id}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultChargecode():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultChargecode] Starting Chargecode validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Chargecode Queue IN"
    str2 = "Chargecode Queue Submit Result"
    
    _log_to_console("  Chargecode Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinchargecode, qsm_chargecode, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Chargecode: Expected '{Transmitter.quinchargecode}' matches Actual '{qsm_chargecode}'\n")
    else:
        _log_to_console(f"    ✗ Chargecode: Expected '{Transmitter.quinchargecode}' does not match Actual '{qsm_chargecode}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultTrxid():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultTrxid] Starting TRX ID validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "TRX ID Queue IN"
    str2 = "TRX ID Queue Submit Result"
    expected_trxid = str(Transmitter.generatediddash)
    
    _log_to_console("  TRX ID Validation Results:\n")
    result = Transmitter.MetchingData(expected_trxid, qsm_trxid, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ TRX ID: Expected '{expected_trxid}' matches Actual '{qsm_trxid}'\n")
    else:
        _log_to_console(f"    ✗ TRX ID: Expected '{expected_trxid}' does not match Actual '{qsm_trxid}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultClientId():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultClientId] Starting Client ID validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Client ID Queue IN"
    str2 = "Client ID Queue Submit Result"
    
    _log_to_console("  Client ID Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinclientid, qsm_client_id, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Client ID: Expected '{Transmitter.quinclientid}' matches Actual '{qsm_client_id}'\n")
    else:
        _log_to_console(f"    ✗ Client ID: Expected '{Transmitter.quinclientid}' does not match Actual '{qsm_client_id}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultChannelMqName():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultChannelMqName] Starting Channel MQ Name validation...\n")
    _log_to_console(separator + "\n")
    
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
    
    _log_to_console("  Channel MQ Name Validation Results:\n")
    result = Transmitter.MetchingData(c_mqname, qsm_channel_mq_name, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Channel MQ Name: Expected '{c_mqname}' matches Actual '{qsm_channel_mq_name}'\n")
    else:
        _log_to_console(f"    ✗ Channel MQ Name: Expected '{c_mqname}' does not match Actual '{qsm_channel_mq_name}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultChannelIsDirect():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultChannelIsDirect] Starting Channel Is Direct validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Client ID Queue IN"
    str2 = "Client ID Queue Submit Result"
    if (getattr(Transmitter, 'senderids_support', 'false') == 'true'):
        c_channelisdirect = str(Transmitter.sid_queue_isdirect)
    else:
        c_channelisdirect = ''
    
    _log_to_console("  Channel Is Direct Validation Results:\n")
    result = Transmitter.MetchingData(c_channelisdirect, qsm_channel_is_direct, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Channel Is Direct: Expected '{c_channelisdirect}' matches Actual '{qsm_channel_is_direct}'\n")
    else:
        _log_to_console(f"    ✗ Channel Is Direct: Expected '{c_channelisdirect}' does not match Actual '{qsm_channel_is_direct}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultDuration():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultDuration] Starting Duration validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Duration"
    str2 = "Duration"
    
    _log_to_console("  Duration Validation Results:\n")
    result = Transmitter.MetchingData(1, 1, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Duration: Expected '1' matches Actual '1'\n")
    else:
        _log_to_console(f"    ✗ Duration: Expected '1' does not match Actual '1'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultServiceType():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultServiceType] Starting Service Type validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Service Type Queue IN"
    str2 = "Service Type Queue Submit Result"
    
    _log_to_console("  Service Type Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinservicetype, qsm_service_type, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Service Type: Expected '{Transmitter.quinservicetype}' matches Actual '{qsm_service_type}'\n")
    else:
        _log_to_console(f"    ✗ Service Type: Expected '{Transmitter.quinservicetype}' does not match Actual '{qsm_service_type}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultWithoutDr():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultWithoutDr] Starting Without DR validation...\n")
    _log_to_console(separator + "\n")
    
    if(Transmitter.cfg_provider_hasdr == 'true'):
        without_dr = 'false'
    else:
        without_dr = 'true'
    str1 = "Without DR Config Transmitter"
    str2 = "Without DR Queue Submit Result"
    
    _log_to_console("  Without DR Validation Results:\n")
    result = Transmitter.MetchingData(without_dr, qsm_without_dr, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Without DR: Expected '{without_dr}' matches Actual '{qsm_without_dr}'\n")
    else:
        _log_to_console(f"    ✗ Without DR: Expected '{without_dr}' does not match Actual '{qsm_without_dr}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultJobId():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultJobId] Starting Job ID validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Job ID Queue In"
    str2 = "Job ID Queue Submit Result"
    
    _log_to_console("  Job ID Validation Results:\n")
    result = Transmitter.MetchingData(
        Transmitter.generatedid, qsm_job_id, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Job ID: Expected '{Transmitter.generatedid}' matches Actual '{qsm_job_id}'\n")
    else:
        _log_to_console(f"    ✗ Job ID: Expected '{Transmitter.generatedid}' does not match Actual '{qsm_job_id}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultMaskName():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultMaskName] Starting Mask Name validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Mask Name Queue IN"
    str2 = "Mask Name Queue Submit Result"
    
    _log_to_console("  Mask Name Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinsender, qsm_mask_name, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Mask Name: Expected '{Transmitter.quinsender}' matches Actual '{qsm_mask_name}'\n")
    else:
        _log_to_console(f"    ✗ Mask Name: Expected '{Transmitter.quinsender}' does not match Actual '{qsm_mask_name}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultProviderId():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultProviderId] Starting Provider ID validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Provider ID Queue IN"
    str2 = "Provider ID Queue Submit Result"
    
    _log_to_console("  Provider ID Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinproviderid, qsm_provider_id, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Provider ID: Expected '{Transmitter.quinproviderid}' matches Actual '{qsm_provider_id}'\n")
    else:
        _log_to_console(f"    ✗ Provider ID: Expected '{Transmitter.quinproviderid}' does not match Actual '{qsm_provider_id}'\n")
    
    _log_to_console(separator + "\n")
    return (result)

def CheckVallueSubmitResultProviderName():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultProviderName] Starting Provider Name validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Provider Name Queue IN"
    str2 = "Provider Name Queue Submit Result"
    
    _log_to_console("  Provider Name Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.cfg_channel_name, qsm_provider_name, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Provider Name: Expected '{Transmitter.cfg_channel_name}' matches Actual '{qsm_provider_name}'\n")
    else:
        _log_to_console(f"    ✗ Provider Name: Expected '{Transmitter.cfg_channel_name}' does not match Actual '{qsm_provider_name}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultMaskId():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultMaskId] Starting Mask ID validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "MaskId"
    str2 = "MaskId"
    
    _log_to_console("  Mask ID Validation Results:\n")
    result = Transmitter.MetchingData("", qsm_mask_id, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Mask ID: Expected '' matches Actual '{qsm_mask_id}'\n")
    else:
        _log_to_console(f"    ✗ Mask ID: Expected '' does not match Actual '{qsm_mask_id}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultMessageSeq():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultMessageSeq] Starting Message Sequence validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Message Sequence Queue IN"
    str2 = "Message Sequence Queue Submit Result"
    
    _log_to_console("  Message Sequence Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinsmspartition, qsm_message_seq, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Message Sequence: Expected '{Transmitter.quinsmspartition}' matches Actual '{qsm_message_seq}'\n")
    else:
        _log_to_console(f"    ✗ Message Sequence: Expected '{Transmitter.quinsmspartition}' does not match Actual '{qsm_message_seq}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultRetry():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultRetry] Starting Retry validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Retry"
    str2 = "Retry"
    
    _log_to_console("  Retry Validation Results:\n")
    result = Transmitter.MetchingData(1, 1, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Retry: Expected '1' matches Actual '1'\n")
    else:
        _log_to_console(f"    ✗ Retry: Expected '1' does not match Actual '1'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultPriorityHeader():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultPriorityHeader] Starting Priority Header validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Priority Header Queue IN"
    str2 = "Priority Header Queue Submit Result"
    
    _log_to_console("  Priority Header Validation Results:\n")
    result = Transmitter.MetchingData('4', qsm_priority_header, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Priority Header: Expected '4' matches Actual '{qsm_priority_header}'\n")
    else:
        _log_to_console(f"    ✗ Priority Header: Expected '4' does not match Actual '{qsm_priority_header}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueSubmitResultPersistent():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueSubmitResultPersistent] Starting Persistent validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Persistent Queue IN"
    str2 = "Persistent Queue Submit Result"
    
    _log_to_console("  Persistent Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.cfg_queue_persistency, qsm_persistent, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Persistent: Expected '{Transmitter.cfg_queue_persistency}' matches Actual '{qsm_persistent}'\n")
    else:
        _log_to_console(f"    ✗ Persistent: Expected '{Transmitter.cfg_queue_persistency}' does not match Actual '{qsm_persistent}'\n")
    
    _log_to_console(separator + "\n")
    return (result)

# def CheckVallueSubmitResult():
