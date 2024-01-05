import Transmitter
import urllib
import sys
import os
import pymysql
from datetime import datetime, timedelta

sys.path.append(os.path.abspath("py/conf"))
# from conf_tsel import *
from config import *

sys.path.append(os.path.abspath("py"))
import TransmitterRedirect


def CountSubmitResult():
    con = pymysql.connect(db=db, user=user, passwd=passwd,
                          host=host, port=3306, autocommit=False)
    cur = con.cursor()
    sql = "SELECT count(*) from out_submitresult where idproccess =  %s"
    query = cur.execute(sql, (txprefname + idproccess))
    resultDB = cur.fetchone()
    return resultDB[0]


def GetDataSubmitResult():
    con = pymysql.connect(db=db, user=user, passwd=passwd,
                          host=host, port=3306, autocommit=False)
    cur = con.cursor()
    sql = "SELECT dateinserted FROM out_submitresult where idproccess =  %s"
    query = cur.execute(sql, (txprefname + idproccess))
    resultDB = cur.fetchall()
    resultDB = [x[0] for x in resultDB]
    return resultDB

def CheckSleepMode():
    str1 = "Time Inqueue Transaction 1 "
    str2 = "Time Inqueue Transaction 2 "
    deltatime = int(Transmitter.cfg_sleep_after_send) / 1000
    print(deltatime)
    if (Transmitter.queuename == queue247):
        count = CountSubmitResult()
        list = GetDataSubmitResult()
    else:
        count = TransmitterRedirect.CountReDirectTransmitters()
        list = TransmitterRedirect.GetDataReDirectTransmitters()
    if(count > 1):
        c = 1
        while c < 10:
            time1 = list[c - 1]
            time2 = list[c]
            time3 = list[c] - timedelta(seconds=int(deltatime))
            timetlr = list[c] - timedelta(seconds=int(deltatime + 1))
            if(time1 == time3 or time1 == timetlr):
                c += 1
                result = {
                    "status": "OK",
                    "message": (str1 + str(time1) + ' & ' + str2 + str(time2)+' Sleep Mode =' + str(deltatime))
                }
                print(result)
            else:
                result = {
                    "status": "NOK",
                    "message": ("Data Tidak Sesuai !! Sample No " + str(c) + ' ' + str1 + str(time1) + ' & ' + str2 + str(time2) + ' Sleep Mode =' + str(deltatime))
                }
                break
    else:
        result = {
            "status": "NOK",
            "message": "Data Tidak Ada"
        }
    return (result)
