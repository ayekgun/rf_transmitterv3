import os
import sys
import json
import urllib.request
import base64
from datetime import datetime
import paramiko

try:
    from robot.api import logger
except ImportError:
    logger = None

sys.path.append(os.path.abspath("py"))
import Transmitter

# Globals for storing retrieved DR Pull registration document
drpull_body = {}
drpull_collection = ""
drpull_type = ""
drpull_docs = {}
drpull_ttl = {}

def _log_to_console(msg):
    sys.stdout.write(msg + "\n")
    sys.stderr.write(msg + "\n")
    sys.stdout.flush()
    sys.stderr.flush()

def _log_chunked(title, content, chunk_size=4000):
    content_str = str(content)
    if logger:
        logger.info(f"=== {title} (Length: {len(content_str)}) ===")
        for i in range(0, len(content_str), chunk_size):
            chunk = content_str[i:i + chunk_size]
            logger.info(f"[{title} Part {i//chunk_size + 1}]\n{chunk}")
    _log_to_console(f"[{title}]\n{content_str}")

def SetVariableQueueDrPullRegistration():
    """
    Retrieves the DR Pull registration message published to ActiveMQ queue 'jns.db.mongodbv2'
    by matching trxid == Transmitter.quinmessageid.
    """
    global drpull_body, drpull_collection, drpull_type, drpull_docs, drpull_ttl
    
    target_trxid = Transmitter.quinmessageid
    _log_to_console(f"[SetVariableQueueDrPullRegistration] Polling ActiveMQ jns.db.mongodbv2 for trxid: {target_trxid}")
    
    hosts = [
        ("192.168.181.51", "admin", "admin"),
        ("192.168.181.58", "admin", "JAtis123!@#")
    ]
    
    found_msg = None
    import time
    for attempt in range(1, 6):
        for host, user, pwd in hosts:
            try:
                url = f"http://{host}:8161/api/jolokia/exec/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=jns.db.mongodbv2/browse()"
                req = urllib.request.Request(url)
                auth = base64.b64encode(f"{user}:{pwd}".encode("ascii")).decode("ascii")
                req.add_header("Authorization", f"Basic {auth}")
                
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    msgs = data.get('value', [])
                    
                    for m in reversed(msgs):
                        try:
                            body = json.loads(m.get('Text', '{}'))
                            docs = {d['key']: d['value'] for d in body.get('documents', [])}
                            if docs.get('trxid') == target_trxid:
                                found_msg = body
                                break
                        except Exception:
                            continue
                if found_msg:
                    break
            except Exception as e:
                _log_to_console(f"[SetVariableQueueDrPullRegistration] Error checking {host}: {e}")
                continue
        if found_msg:
            break
        time.sleep(1)
        
    if not found_msg:
        err = f"DR Pull registration message not found in ActiveMQ queue 'jns.db.mongodbv2' for trxid={target_trxid}"
        _log_chunked("ERROR NOT FOUND", err)
        return {"status": "NOK", "message": err}
        
    drpull_body = found_msg
    drpull_collection = found_msg.get('collection', '')
    drpull_type = found_msg.get('type', '')
    drpull_docs = {d['key']: d['value'] for d in found_msg.get('documents', [])}
    drpull_ttl = {t['key']: t['value'] for t in found_msg.get('ttl', [])}
    
    _log_chunked("[ACTUAL PAYLOAD - DR PULL REGISTRATION]", json.dumps(found_msg, indent=2))
    return {"status": "OK", "message": "Successfully retrieved DR Pull registration from jns.db.mongodbv2"}

def CheckDrPullCollectionAndType():
    """Validates collection == 'dr_pull_telkomsel' and type == 'insert'"""
    expected = {"collection": "dr_pull_telkomsel", "type": "insert"}
    actual = {"collection": drpull_collection, "type": drpull_type}
    
    _log_chunked("[EXPECTED PAYLOAD - COLLECTION & TYPE]", json.dumps(expected, indent=2))
    _log_chunked("[ACTUAL PAYLOAD - COLLECTION & TYPE]", json.dumps(actual, indent=2))
    
    if drpull_collection != expected["collection"] or drpull_type != expected["type"]:
        res = f"Mismatch: expected {expected}, got {actual}"
        _log_chunked("[COMPARISON RESULT - COLLECTION & TYPE]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    _log_chunked("[COMPARISON RESULT - COLLECTION & TYPE]", "PASS - Collection and type match expected contract")
    return {"status": "OK", "message": "Collection and type match expected contract"}

def CheckDrPullDocumentsStatusPending():
    """Validates status == 'PENDING' and attempt == '0'"""
    expected = {"status": "PENDING", "attempt": "0"}
    actual = {"status": drpull_docs.get("status"), "attempt": drpull_docs.get("attempt")}
    
    _log_chunked("[EXPECTED PAYLOAD - STATUS & ATTEMPT]", json.dumps(expected, indent=2))
    _log_chunked("[ACTUAL PAYLOAD - STATUS & ATTEMPT]", json.dumps(actual, indent=2))
    
    if actual["status"] != expected["status"] or str(actual["attempt"]) != expected["attempt"]:
        res = f"Mismatch: expected {expected}, got {actual}"
        _log_chunked("[COMPARISON RESULT - STATUS & ATTEMPT]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    _log_chunked("[COMPARISON RESULT - STATUS & ATTEMPT]", "PASS - Status is PENDING and initial attempt is 0")
    return {"status": "OK", "message": "Status is PENDING and initial attempt is 0"}

def CheckDrPullDocumentsIdentifiers():
    """Validates trxid, msisdn, channel_name, provider_id, appsid, sid, provider_trxid"""
    expected = {
        "trxid": Transmitter.quinmessageid,
        "msisdn": Transmitter.quinmsisdn,
        "channel_name": "TSEL",
        "provider_id": "1",
        "appsid": "QueueUID",
        "sid": "QueueSenderID"
    }
    
    actual = {
        "trxid": drpull_docs.get("trxid"),
        "msisdn": drpull_docs.get("msisdn"),
        "channel_name": drpull_docs.get("channel_name"),
        "provider_id": str(drpull_docs.get("provider_id")),
        "appsid": drpull_docs.get("appsid"),
        "sid": drpull_docs.get("sid"),
        "provider_trxid": drpull_docs.get("provider_trxid")
    }
    
    _log_chunked("[EXPECTED PAYLOAD - DOCUMENT IDENTIFIERS]", json.dumps(expected, indent=2))
    _log_chunked("[ACTUAL PAYLOAD - DOCUMENT IDENTIFIERS]", json.dumps(actual, indent=2))
    
    mismatches = []
    for k, v in expected.items():
        if actual.get(k) != v:
            mismatches.append(f"{k}: expected '{v}', got '{actual.get(k)}'")
            
    if not actual.get("provider_trxid"):
        mismatches.append("provider_trxid is empty")
        
    if mismatches:
        res = "; ".join(mismatches)
        _log_chunked("[COMPARISON RESULT - DOCUMENT IDENTIFIERS]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    _log_chunked("[COMPARISON RESULT - DOCUMENT IDENTIFIERS]", "PASS - All document identifiers match expected values")
    return {"status": "OK", "message": "All document identifiers match expected values"}

def CheckDrPullNextPullSchedule():
    """
    Validates submit_date format and verifies that next_pull_at is scheduled
    exactly 2 minutes (+120 seconds) after submit_date.
    """
    submit_date_str = drpull_docs.get("submit_date")
    date_created_str = drpull_ttl.get("date_created")
    next_pull_at_str = drpull_ttl.get("next_pull_at")
    
    expected = {
        "delay_minutes": 2,
        "date_created": submit_date_str
    }
    actual = {
        "submit_date": submit_date_str,
        "date_created": date_created_str,
        "next_pull_at": next_pull_at_str
    }
    
    _log_chunked("[EXPECTED PAYLOAD - SCHEDULE]", json.dumps(expected, indent=2))
    _log_chunked("[ACTUAL PAYLOAD - SCHEDULE]", json.dumps(actual, indent=2))
    
    try:
        dt_submit = datetime.strptime(submit_date_str, "%Y-%m-%d %H:%M:%S")
        dt_created = datetime.strptime(date_created_str, "%Y-%m-%d %H:%M:%S")
        dt_next = datetime.strptime(next_pull_at_str, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        res = f"Date parsing error: {e}"
        _log_chunked("[COMPARISON RESULT - SCHEDULE]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    if dt_submit != dt_created:
        res = f"date_created ({date_created_str}) does not match submit_date ({submit_date_str})"
        _log_chunked("[COMPARISON RESULT - SCHEDULE]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    diff_seconds = (dt_next - dt_submit).total_seconds()
    if diff_seconds != 120:
        res = f"Expected next_pull_at delay of 120s (+2 mins), got {diff_seconds}s difference"
        _log_chunked("[COMPARISON RESULT - SCHEDULE]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    _log_chunked("[COMPARISON RESULT - SCHEDULE]", f"PASS - next_pull_at is scheduled exactly +120s (2 minutes) after submit_date")
    return {"status": "OK", "message": f"next_pull_at is scheduled exactly +120s (2 minutes) after submit_date"}

def CheckDrPullSutLogTrace():
    """
    Connects to SUT host and validates that SUT logged:
    '[registerDrPull] publish PENDING provider_trxid=<trxid> to queue jns.db.mongodbv2'
    """
    target_trxid = Transmitter.quinmessageid
    hosts = [
        ("192.168.181.51", "dockersit123", "/var/opt/JNS6.5/Transmitter_jns6.5/TransmitterTelkomselV2"),
        ("192.168.181.58", "dockersit123", "/var/opt/JNS.6.5/TransmitterTelkomselV2")
    ]
    
    found_trace = False
    log_line = ""
    for host, pwd, base_dir in hosts:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username="root", password=pwd, timeout=4)
            cmd = f"grep '{target_trxid}' {base_dir}/log/transmittertelkomsel_reg247/transmittertelkomsel_reg247.debug.log | grep 'registerDrPull'"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode().strip()
            ssh.close()
            if "publish PENDING provider_trxid=" in out:
                found_trace = True
                log_line = out
                break
        except Exception:
            continue
            
    _log_chunked("[EXPECTED SUT LOG PATTERN]", f"[registerDrPull] publish PENDING provider_trxid=... to queue jns.db.mongodbv2 with trxid={target_trxid}")
    _log_chunked("[ACTUAL SUT LOG LINE]", log_line if found_trace else "NOT FOUND")
    
    if not found_trace:
        res = f"SUT debug log trace not found for trxid={target_trxid}"
        _log_chunked("[COMPARISON RESULT - SUT LOG TRACE]", f"FAILED - {res}")
        return {"status": "NOK", "message": res}
        
    _log_chunked("[COMPARISON RESULT - SUT LOG TRACE]", f"PASS - Found SUT registerDrPull log line: {log_line}")
    return {"status": "OK", "message": "Found SUT registerDrPull log line"}
