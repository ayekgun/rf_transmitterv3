import os
import time
import sys
import urllib.parse
import stomp
import pymysql
from datetime import datetime, timedelta
import requests

sys.path.append(os.path.abspath("py/conf"))
from config import *

def _unpack_msg(args):
    if len(args) == 1:
        frame = args[0]
        return getattr(frame, 'headers', {}), getattr(frame, 'body', '')
    elif len(args) >= 2:
        return args[0], args[1]
    return {}, ''

class MyListenerTransmitter(stomp.ConnectionListener):
    def on_error(self, *args):
        headers, message = _unpack_msg(args)
        print('received an error "%s"' % headers)
    def on_message(self, *args):
        headers, message = _unpack_msg(args)
        print('received a message "%s"' % (message))
        trxid = (urllib.parse.parse_qs(message , keep_blank_values=True)['trxid'][0])
        messageid = (urllib.parse.parse_qs(message , keep_blank_values=True)['messageid'][0])
        msisdn = (urllib.parse.parse_qs(message , keep_blank_values=True)['msisdn'][0])
        message_sms = (urllib.parse.parse_qs(message , keep_blank_values=True)['message'][0])
        batchname = (urllib.parse.parse_qs(message , keep_blank_values=True)['batchname'][0])
        clientid = (urllib.parse.parse_qs(message , keep_blank_values=True)['clientid'][0])
        divisionid = (urllib.parse.parse_qs(message , keep_blank_values=True)['divisionid'][0])
        senderid = (urllib.parse.parse_qs(message , keep_blank_values=True)['senderid'][0])
        uid = (urllib.parse.parse_qs(message , keep_blank_values=True)['uid'][0])
        pwd = (urllib.parse.parse_qs(message , keep_blank_values=True)['pwd'][0])
        cpName = (urllib.parse.parse_qs(message , keep_blank_values=True)['cpName'][0])
        uploadby = (urllib.parse.parse_qs(message , keep_blank_values=True)['uploadby'][0])
        approveby = (urllib.parse.parse_qs(message , keep_blank_values=True)['approveby'][0])
        dateupload = (urllib.parse.parse_qs(message , keep_blank_values=True)['dateupload'][0])
        dateapprove = (urllib.parse.parse_qs(message , keep_blank_values=True)['dateapprove'][0])
        dateinqueue = (urllib.parse.parse_qs(message , keep_blank_values=True)['dateinqueue'][0])
        servicetype = (urllib.parse.parse_qs(message , keep_blank_values=True)['servicetype'][0])
        providerid = (urllib.parse.parse_qs(message , keep_blank_values=True)['providerid'][0])
        billable = (urllib.parse.parse_qs(message , keep_blank_values=True)['billable'][0])
        jatismessageid = (urllib.parse.parse_qs(message , keep_blank_values=True)['jatismessageid'][0])
        uploadtype = (urllib.parse.parse_qs(message , keep_blank_values=True)['uploadtype'][0])
        smspartition = (urllib.parse.parse_qs(message , keep_blank_values=True)['smspartition'][0])
        expiry = (urllib.parse.parse_qs(message , keep_blank_values=True)['expiry'][0])
        sender = (urllib.parse.parse_qs(message , keep_blank_values=True)['sender'][0])
        channel_mq_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['channel_mq_name'][0])
        priority = (urllib.parse.parse_qs(message , keep_blank_values=True)['priority'][0])
        adddata1 = (urllib.parse.parse_qs(message , keep_blank_values=True)['adddata1'][0])
        adddata2 = (urllib.parse.parse_qs(message , keep_blank_values=True)['adddata2'][0])
        adddata3 = (urllib.parse.parse_qs(message , keep_blank_values=True)['adddata3'][0])
        chargecode = (urllib.parse.parse_qs(message , keep_blank_values=True)['chargecode'][0])

        persistent = headers.get('persistent' , 'false')
        timestamp = headers.get('timestamp')
        # origin_mq_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['origin_mq_name'][1])
        priority_header = headers.get('priority', '4')
        try:
            senderids = (urllib.parse.parse_qs(message , keep_blank_values=True)['senderids'][0])
        except:
            senderids = ''
        try:
            origin_mq_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['origin_mq_name'][-1])
        except:
            origin_mq_name = ''
        con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute("insert into out_transmitter_redirect values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(trxid,messageid,msisdn,message_sms,batchname,clientid,divisionid,senderid,uid,pwd,cpName,uploadby,approveby,dateupload,dateapprove,dateinqueue,servicetype,providerid,billable,jatismessageid,uploadtype,smspartition,expiry,sender,channel_mq_name,priority,adddata1,adddata2,adddata3,chargecode,senderids,priority_header,persistent,origin_mq_name,prefname + idproccess,datesend,datetime.fromtimestamp( int(timestamp) / 1000.0)))
        con.commit()
        cur.close()

class MyListenerSubmitResult(stomp.ConnectionListener):
    def on_error(self, *args):
        headers, message = _unpack_msg(args)
        print('received an error "%s"' % headers)
    def on_message(self, *args):
        headers, message = _unpack_msg(args)
        print('received a message "%s"' % (message))
        channel_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['channel_name'][0])
        provider_submit_status = str((urllib.parse.parse_qs(message , keep_blank_values=True)['provider_submit_status'][0]))
        print(str(provider_submit_status))
        date_hit = (urllib.parse.parse_qs(message , keep_blank_values=True)['date_hit'][0])
        transmitter_submit_status = (urllib.parse.parse_qs(message , keep_blank_values=True)['transmitter_submit_status'][0])
        date_response = (urllib.parse.parse_qs(message , keep_blank_values=True)['date_response'][0])
        division_id = (urllib.parse.parse_qs(message , keep_blank_values=True)['division_id'][0])
        chargecode = (urllib.parse.parse_qs(message , keep_blank_values=True)['chargecode'][0])
        trxid = (urllib.parse.parse_qs(message , keep_blank_values=True)['trxid'][0])
        client_id = (urllib.parse.parse_qs(message , keep_blank_values=True)['client_id'][0])
        channel_mq_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['channel_mq_name'][0])
        duration = (urllib.parse.parse_qs(message , keep_blank_values=True)['duration'][0])
        service_type = (urllib.parse.parse_qs(message , keep_blank_values=True)['service_type'][0])
        without_dr = (urllib.parse.parse_qs(message , keep_blank_values=True)['without_dr'][0])
        job_id = (urllib.parse.parse_qs(message , keep_blank_values=True)['job_id'][0])
        mask_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['mask_name'][0])
        provider_id = (urllib.parse.parse_qs(message , keep_blank_values=True)['provider_id'][0])
        provider_trxid = (urllib.parse.parse_qs(message , keep_blank_values=True)['provider_trxid'][0])
        provider_name = (urllib.parse.parse_qs(message , keep_blank_values=True)['provider_name'][0])
        mask_id = (urllib.parse.parse_qs(message , keep_blank_values=True)['mask_id'][0])
        message_seq = (urllib.parse.parse_qs(message , keep_blank_values=True)['message_seq'][0])
        date_hit =  datetime.strptime(date_hit,'%Y%m%d%H%M%S')
        date_response = datetime.strptime(date_response,'%Y%m%d%H%M%S')
        persistent = headers.get('persistent' , 'false')
        priority_header = headers.get('priority', '4')
        timestamp = headers.get('timestamp')
        try:
            retry = (urllib.parse.parse_qs(message , keep_blank_values=True)['retry'][0])
        except:
            retry = ''
        try:
            channel_is_direct = (urllib.parse.parse_qs(message , keep_blank_values=True)['channel_is_direct'][0])
        except:
            channel_is_direct = ''

        con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute("insert into out_submitresult values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(channel_name,provider_submit_status,date_hit,transmitter_submit_status,date_response,division_id,chargecode,trxid,client_id,channel_mq_name,channel_is_direct,duration,service_type,without_dr,job_id,mask_name,provider_id,provider_trxid,provider_name,mask_id,message_seq,retry,priority_header,persistent,prefname + idproccess,datetime.fromtimestamp( int(timestamp) / 1000.0)))
        con.commit()
        cur.close()

class MyListenerReroute(stomp.ConnectionListener):
    def on_error(self, *args):
        headers, message = _unpack_msg(args)
        print('received an error "%s"' % headers)
    def on_message(self, *args):
        headers, message = _unpack_msg(args)
        print('received a message "%s"' % (message))
        trxid = (urllib.parse.parse_qs(message , keep_blank_values=True)['trxid'][0])
        persistent = headers.get('persistent' , 'false')
        timestamp = headers.get('timestamp')
        con = pymysql.connect(db=db, user=user, passwd=passwd,host=host,port=3306,autocommit=False)
        cur = con.cursor()
        cur.execute(
            "insert into out_reroute_jns (trxid, message, persistent, timestamp) values(%s,%s,%s,%s)",
            (trxid, message, persistent, datetime.fromtimestamp(int(timestamp) / 1000.0))
        )
        con.commit()
        cur.close()

def GetQueueTransmitter(mqname,sleeptime):
    conn = stomp.Connection([(host_amq,port_amq)])
    conn.set_listener('', MyListenerTransmitter())
    if hasattr(conn, 'start'):
        conn.start()
    conn.connect('admin', 'JAtis123!@#', wait=True)
    conn.subscribe(destination="/queue/"+ mqname, id=1, ack='auto')
    #conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')
    time.sleep(sleeptime)
    conn.disconnect()

def GetQueueReroute(mqname,sleeptime):
    conn = stomp.Connection([(host_amq,port_amq)])
    conn.set_listener('', MyListenerReroute())
    if hasattr(conn, 'start'):
        conn.start()
    conn.connect('admin', 'JAtis123!@#', wait=True)
    conn.subscribe(destination="/queue/"+ mqname, id=1, ack='auto')
    #conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')
    time.sleep(sleeptime + 1)
    conn.disconnect()

def GetQueueSubmitResult(mqname,sleeptime):
    conn = stomp.Connection([(host_amq,port_amq)])
    conn.set_listener('', MyListenerSubmitResult())
    if hasattr(conn, 'start'):
        conn.start()
    conn.connect('admin', 'JAtis123!@#', wait=True)
    conn.subscribe(destination="/queue/"+ mqname, id=1, ack='auto')
    #conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')
    time.sleep(sleeptime + 1)
    conn.disconnect()

def _create_stomp_conn(host=None, port=None):
    h = host or host_amq
    p = port or port_amq
    try:
        conn = stomp.Connection([(h, p)], auto_content_length=False)
    except TypeError:
        conn = stomp.Connection([(h, p)])
        try:
            conn.auto_content_length = False
        except Exception:
            pass
    return conn

def SendQueue(queuMessage , destinationqueue, prefix, host=None, port=None):
    global prefname
    global datesend
    prefname = prefix
    datesend = GetDateTimeServer()
    conn = _create_stomp_conn(host, port)
    if hasattr(conn, 'start'):
        conn.start()
    conn.connect('admin', 'JAtis123!@#', wait=True)
    dest = destinationqueue if destinationqueue.startswith('/queue/') else '/queue/' + destinationqueue
    headers = {
        'amq-msg-type': 'text',
        'transformation': 'jms-text'
    }
    conn.send(dest, queuMessage, headers=headers)
    conn.disconnect()

def SendQueueDualSite(queuMessage, destinationqueue, prefix, host_prod=None, host_drc=None):
    h_prod = host_prod or host_amq
    p_prod = port_amq
    h_drc = host_drc or globals().get('host_amq_drc', '192.168.181.58')
    p_drc = globals().get('port_amq_drc', 61613)

    print(f"[SendQueueDualSite] Sending to PROD ({h_prod}:{p_prod})...")
    SendQueue(queuMessage, destinationqueue, prefix, host=h_prod, port=p_prod)

    print(f"[SendQueueDualSite] Sending to DRC ({h_drc}:{p_drc})...")
    SendQueue(queuMessage, destinationqueue, prefix, host=h_drc, port=p_drc)

def SendTopic():
    conn = _create_stomp_conn()
    if hasattr(conn, 'start'):
        conn.start()
    conn.connect('admin', 'JAtis123!@#', wait=True)
    conn.send('/topic/jns6.5-command' , 'reload' , headers={'content-length': None})
    conn.disconnect()

def SendTopicSmartBreake(queuename,msg,direct):
    payload = '{"queName":"'+ queuename +'","message":"'+ msg +'","direct":"'+ direct +'"}'
    conn = _create_stomp_conn()
    if hasattr(conn, 'start'):
        conn.start()
    conn.connect('admin', 'JAtis123!@#', wait=True)
    headers = {
        'content-length': None,
        'transformation': 'jms-text',
        'amq-msg-type': 'text'
    }
    conn.send('/topic/jns.topic.command', payload, headers=headers)
    conn.disconnect()

def GetDateTimeServer():
    url = 'http://192.168.181.51/dateserver.php'
    req = requests.get(url)
    return (req.text)

# if __name__ == '__main__':
#     SendTopicSmartBreake()
