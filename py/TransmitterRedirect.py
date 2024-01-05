import Transmitter
import urllib
from config import *
import pymysql
import time

def SetVariableQueueTransmitterReDirect():
    # time.sleep(int(Transmitter.cfg_sleep_after_send) / 1000 )
    result_Db = GetDataQueueTransmitteReDirect()
    if (result_Db is None):
        result =  {
            "status": "NOK",
            "message": "Data Transaction tidak ada / Tidak Put Queue Transmitter"
            }
    else:
        i = 0
        while i < len(dic_txredirect):
            globals() [dic_txredirect[i]] = result_Db[i]
            i += 1
        result =  {
            "status": "OK",
            "message": "OK"
            }
    return (result)


def GetDataQueueTransmitteReDirect():
    n = 1
    while n <= 3:
        con = pymysql.connect(db=db, user=user, passwd=passwd,
                              host=host, port=3306, autocommit=False)
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM out_transmitter_redirect where  trxid = %s", (Transmitter.quintrxid,))
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

def GetDataReDirectTransmitters():
    con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
    cur = con.cursor()
    sql ="SELECT dateinserted FROM out_transmitter_redirect where idproccess =  %s"
    query = cur.execute(sql ,(txprefname + idproccess))
    resultDB = cur.fetchall()
    resultDB = [x[0] for x in resultDB]
    return resultDB

def CheckVallueMessageid():
    str1 ="Trxid ID From DB Transaction"
    str2 ="Message ID From Queue"
    result = Transmitter.MetchingData(Transmitter.quinmessageid, quotmessageid,str1,str2)
    return (result)

def CheckVallueMsisdn():
    str1 ="Msisdn From DB Transaction"
    str2 ="Msisdn From Queue"
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, quotmsisdn,str1,str2)
    return (result)

def CheckVallueMessage():
    str1 ="Message From DB Transaction"
    str2 ="Message From Queue"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quinmessage), quotmessage,str1,str2)
    return (result)

def CheckVallueBatchname():
    str1 ="FileName From DB Transaction"
    str2 ="Batchname From Queue"
    result = Transmitter.MetchingData(Transmitter.quinbatchname, quotbatchname,str1,str2)
    return (result)

def CheckVallueClientid():
    str1 ="Client ID From DB Transaction"
    str2 ="Client ID From Queue"
    result = Transmitter.MetchingData(int(Transmitter.quinclientid), quotclientid,str1,str2)
    return (result)

def CheckVallueDivisionid():
    str1 ="Division ID From DB Transaction"
    str2 ="Division ID From Queue"
    result = Transmitter.MetchingData(int(Transmitter.quindivisionid), quotdivisionid,str1,str2)
    return (result)

def CheckVallueSenderid():
    str1 ="Sender ID From DB Transaction"
    str2 ="Sender ID From Queue"
    result = Transmitter.MetchingData(Transmitter.quinsenderid, quotsenderid,str1,str2)
    return (result)

def CheckVallueUid():
    str1 ="Uid From DB Transaction"
    str2 ="Uid From Queue"
    result = Transmitter.MetchingData(Transmitter.quinuid, quotuid,str1,str2)
    return (result)

def CheckValluePwd():
    str1 ="Pwd From DB Transaction"
    str2 ="Pwd From Queue"
    result = Transmitter.MetchingData(Transmitter.quinpwd, quotpwd,str1,str2)
    return (result)

def CheckVallueCpName():
    str1 ="CP Name From DB Transaction"
    str2 ="CP Name From Queue"
    result = Transmitter.MetchingData(Transmitter.quincpName, quotcpName,str1,str2)
    return (result)

def CheckVallueUploadby():
    str1 ="UploadBy From DB Transaction"
    str2 ="UploadBy From Queue"
    result = Transmitter.MetchingData(Transmitter.quinuploadby, quotuploadby,str1,str2)
    return (result)

def CheckVallueApproveby():
    str1 ="UploadBy From DB Transaction"
    str2 ="ApprovedBy From Queue"
    result = Transmitter.MetchingData(Transmitter.quinapproveby, quotapproveby,str1,str2)
    return (result)

def CheckVallueDateupload():
    str1 ="ServiceType From DB Transaction"
    str2 ="ServiceType From Queue"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quindateupload), str(quotdateupload),str1,str2)
    return (result)

def CheckVallueDateapprove():
    str1 ="ServiceType From DB Transaction"
    str2 ="ServiceType From Queue"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quindateapprove), str(quotdateapprove),str1,str2)
    return (result)

def CheckVallueDateinqueue():
    str1 ="ServiceType From DB Transaction"
    str2 ="ServiceType From Queue"
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quindateinqueue), str(quotdateinqueue),str1,str2)
    return (result)

def CheckVallueServicetype():
    str1 ="ServiceType From DB Transaction"
    str2 ="ServiceType From Queue"
    result = Transmitter.MetchingData(Transmitter.quinservicetype, quotservicetype,str1,str2)
    return (result)

def CheckVallueProviderid():
    str1 ="Provider ID From DB Transaction"
    str2 ="Provider ID From Queue"
    result = Transmitter.MetchingData(int(Transmitter.quinproviderid), quotproviderid,str1,str2)
    return (result)

def CheckVallueBillable():
    str1 ="Billable From DB Transaction"
    str2 ="Billable From Queue"
    result = Transmitter.MetchingData(int(Transmitter.quinbillable), quotbillable,str1,str2)
    return (result)

def CheckValluejatiSmessageid():
    str1 ="Billable From DB Transaction"
    str2 ="Billable From Queue"
    result = Transmitter.MetchingData(Transmitter.quinjatismessageid, quotjatismessageid,str1,str2)
    return (result)

def CheckValluejatiUploadtype():
    str1 ="Billable From DB Transaction"
    str2 ="Billable From Queue"
    result = Transmitter.MetchingData(Transmitter.quinuploadtype, quotuploadtype,str1,str2)
    return (result)

def CheckVallueSmspartition():
    str1 ="SMS Partition From DB Transaction"
    str2 ="SMS Partition From Queue"
    result = Transmitter.MetchingData(int(Transmitter.quinsmspartition), quotsmspartition,str1,str2)
    return (result)

def CheckVallueExpiry():
    str1 ="Expired from generated by 5 minutes"
    str2 ="Expired From Queue"
    result = Transmitter.MetchingData(Transmitter.quinexpiry, quotexpiry,str1,str2)
    return (result)

def CheckVallueSender():
    str1 ="Mask Name From DB Transaction"
    str2 ="Sender From Queue"
    result = Transmitter.MetchingData(Transmitter.quinsender, quotsender,str1,str2)
    return (result)

def CheckVallueChannel_mq_name():
    str1 ="Channel Mq Name From DB Transaction"
    str2 ="Channel Mq Name From Queue"
    result = Transmitter.MetchingData(Transmitter.quinchannel_mq_name, quotchannel_mq_name,str1,str2)
    return (result)

def CheckValluePriority():
    str1 ="Priority From DB Transaction"
    str2 ="Priority From Queue"
    result = Transmitter.MetchingData(int(Transmitter.quinpriority), quotpriority,str1,str2)
    return (result)

def CheckVallueAdddata1():
    str1 ="Priority From DB Transaction"
    str2 ="Priority From Queue"
    result = Transmitter.MetchingData(Transmitter.quinadddata1, quotadddata1,str1,str2)
    return (result)

def CheckVallueAdddata2():
    str1 ="Priority From DB Transaction"
    str2 ="Priority From Queue"
    result = Transmitter.MetchingData(Transmitter.quinadddata2, quotadddata2,str1,str2)
    return (result)

def CheckVallueAdddata3():
    str1 ="Priority From DB Transaction"
    str2 ="Priority From Queue"
    result = Transmitter.MetchingData(Transmitter.quinadddata3, quotadddata3,str1,str2)
    return (result)

def CheckVallueChargecode():
    str1 ="ChargeCode From M2M"
    str2 ="ChargeCode From Queue"
    result = Transmitter.MetchingData(Transmitter.quinchargecode, quotchargecode,str1,str2)
    return (result)

def CheckVallueSenderids():
    str1 ="ChargeCode From M2M"
    str2 ="ChargeCode From Queue"
    #result = Transmitter.MetchingData(chargecode, quchargecode,str1,str2)
    result = Transmitter.MetchingData(urllib.parse.unquote_plus(Transmitter.quinsenderids),quotsenderids,str1,str2)
    return (result)

def CheckValluePriority_header():
    str1 ="Priority From DB Transaction"
    str2 ="Priority From Queue"
    result = Transmitter.MetchingData(quotpriority, quotpriority_header,str1,str2)
    return (result)

def CheckValluePersistent():
    str1 ="Persistent From Config Lookup"
    str2 ="Persistent From Queue"
    result = Transmitter.MetchingData(Transmitter.cfg_queue_persistency, quotpersistent,str1,str2)
    return (result)

def CheckVallueOriginmqname():
    str1 ="Origin MQ Name from DB"
    str2 ="Origin MQ Name from Queue"
    result = Transmitter.MetchingData(
        Transmitter.queuename, quotorigin_mq_name, str1, str2)
    return (result)
