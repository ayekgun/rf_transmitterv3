import os
import sys
import Transmitter
import requests
import json
import urllib
import time
from datetime import datetime, timedelta

sys.path.append(os.path.abspath("py/conf"))
from config import *

sys.path.append(os.path.abspath("py/lib/mongodb"))
from MongoJNS import *
mg = mongo()


def SetVariableResponeResultJantara():
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        result = {
            "status": "OK",
            "message": "Baypas Telco / Langsung masuk Submit Result"
        }
    else:
        json_data = GetResultDummyWithApiJantara()
        if (json_data == 'Data Not Found'):
            result = {
                "status": "NOK",
                "message": "Data Telco tidak ada / Tidak Hit Telco"
            }
        else:
            
            global t_message
            global t_respontrxid
            global t_responstatus
            global t_username
            global t_password
            global t_command
            global t_ani
            global t_dnis
            global t_dataCoding
            global t_longMessageMode
            
            # Parse new JSON parameters
            t_username = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['username'][0])
            t_password = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['password'][0])
            t_command = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['command'][0])
            t_ani = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['ani'][0])
            t_dnis = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['dnis'][0])
            t_message = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True)['message'][0])
            t_dataCoding = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True).get('dataCoding', [None])[0])
            t_longMessageMode = (urllib.parse.parse_qs(
                json_data['parameter'], keep_blank_values=True).get('longMessageMode', [None])[0])
            t_respontrxid = json_data['provider_trxid']
            t_responstatus = json_data['respon']
            result = {
                "status": "OK",
                "message": "OK"
            }
    return result


def GetResultDummyWithApiJantara():
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
    print(result)
    return result

def CheckVallueANITelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueANITelcoJantara] Starting ANI validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "ANI From DB Config"
    str2 = "ANI From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_senderid != ''):
            c_sid = Transmitter.sid_queue_senderid
        else:
            c_sid = ''
    else:
        if(Transmitter.quinsenderid != ''):
            c_sid = Transmitter.quinsenderid
        else:
            c_sid = ''
    
    _log_to_console("  ANI Validation Results:\n")
    result = Transmitter.MetchingData(c_sid, t_ani, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ ANI: Expected '{c_sid}' matches Actual '{t_ani}'\n")
    else:
        _log_to_console(f"    ✗ ANI: Expected '{c_sid}' does not match Actual '{t_ani}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueDataCodingTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueDataCodingTelcoJantara] Starting Data Coding validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Data Coding From DB Expected"
    str2 = "Data Coding From TelcoReceiver Actual"
    # If t_dataCoding is None or empty, convert to empty string
    expected_value = None  # Expected value bisa None jika tidak dikirim
    actual_value = t_dataCoding if t_dataCoding is not None else None
    
    _log_to_console("  Data Coding Validation Results:\n")
    result = Transmitter.MetchingData(expected_value, actual_value, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Data Coding: Expected '{expected_value}' matches Actual '{actual_value}'\n")
    else:
        _log_to_console(f"    ✗ Data Coding: Expected '{expected_value}' does not match Actual '{actual_value}'\n")
    
    _log_to_console(separator + "\n")
    return (result)

def CheckVallueDNISTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueDNISTelcoJantara] Starting DNIS validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "DNIS From Queue"
    str2 = "DNIS From TelcoReceiver"
    
    _log_to_console("  DNIS Validation Results:\n")
    result = Transmitter.MetchingData(Transmitter.quinmsisdn, t_dnis, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ DNIS: Expected '{Transmitter.quinmsisdn}' matches Actual '{t_dnis}'\n")
    else:
        _log_to_console(f"    ✗ DNIS: Expected '{Transmitter.quinmsisdn}' does not match Actual '{t_dnis}'\n")
    
    _log_to_console(separator + "\n")
    return (result)

def CheckVallueLongMessageModeTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueLongMessageModeTelcoJantara] Starting Long Message Mode validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Long Message Mode From DB Expected"
    str2 = "Long Message Mode From TelcoReceiver Actual"
    # Calculate expected value based on message length
    message_decoded = urllib.parse.unquote_plus(Transmitter.quinmessage)
    message_length = len(message_decoded)
    
    if message_length > 160:
        expected_value = "split"
    else:
        expected_value = "payload"
    actual_value = t_longMessageMode if t_longMessageMode is not None else None
    
    _log_to_console("  Long Message Mode Validation Results:\n")
    _log_to_console(f"    Message length: {message_length} characters\n")
    result = Transmitter.MetchingData(expected_value, actual_value, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Long Message Mode: Expected '{expected_value}' (message length {'>' if message_length > 160 else '<='} 160) matches Actual '{actual_value}'\n")
    else:
        _log_to_console(f"    ✗ Long Message Mode: Expected '{expected_value}' (message length {'>' if message_length > 160 else '<='} 160) does not match Actual '{actual_value}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueMessageTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueMessageTelcoJantara] Starting Message validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Message From DB Config"
    str2 = "Message From TelcoReceiver"
    expected_msg = urllib.parse.unquote_plus(Transmitter.quinmessage)
    actual_msg = urllib.parse.unquote_plus(t_message)
    
    _log_to_console("  Message Validation Results:\n")
    result = Transmitter.MetchingData(expected_msg, actual_msg, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Message: Expected length {len(expected_msg)} matches Actual length {len(actual_msg)}\n")
        _log_to_console(f"      Expected preview: {expected_msg[:80]}{'...' if len(expected_msg) > 80 else ''}\n")
        _log_to_console(f"      Actual preview: {actual_msg[:80]}{'...' if len(actual_msg) > 80 else ''}\n")
    else:
        _log_to_console(f"    ✗ Message: Expected length {len(expected_msg)} does not match Actual length {len(actual_msg)}\n")
        _log_to_console(f"      Expected preview: {expected_msg[:80]}{'...' if len(expected_msg) > 80 else ''}\n")
        _log_to_console(f"      Actual preview: {actual_msg[:80]}{'...' if len(actual_msg) > 80 else ''}\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckVallueCommandTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueCommandTelcoJantara] Starting Command validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Command From DB Expected"
    str2 = "Command From TelcoReceiver Actual"
    
    _log_to_console("  Command Validation Results:\n")
    result = Transmitter.MetchingData("submit", t_command, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Command: Expected 'submit' matches Actual '{t_command}'\n")
    else:
        _log_to_console(f"    ✗ Command: Expected 'submit' does not match Actual '{t_command}'\n")
    
    _log_to_console(separator + "\n")
    return (result)

def CheckVallueUsernameTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckVallueUsernameTelcoJantara] Starting Username validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Username From DB Config"
    str2 = "Username From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_username != ''):
            c_username = Transmitter.sid_queue_username
        else:
            c_username = Transmitter.cfg_username
    else:
        if(Transmitter.quinuid != ''):
            c_username = Transmitter.quinuid
        else:
            c_username = Transmitter.cfg_username
    
    _log_to_console("  Username Validation Results:\n")
    result = Transmitter.MetchingData(c_username, t_username, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Username: Expected '{c_username}' matches Actual '{t_username}'\n")
    else:
        _log_to_console(f"    ✗ Username: Expected '{c_username}' does not match Actual '{t_username}'\n")
    
    _log_to_console(separator + "\n")
    return (result)


def CheckValluePasswordTelcoJantara():
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckValluePasswordTelcoJantara] Starting Password validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "Password From DB Config"
    str2 = "Password From TelcoReceiver"
    if (Transmitter.senderids_support == 'true'):
        if(Transmitter.sid_queue_password != ''):
            c_password = Transmitter.sid_queue_password
        else:
            c_password = Transmitter.cfg_password
    else:
        if(Transmitter.quinpwd != ''):
            c_password = Transmitter.quinpwd
        else:
            c_password = Transmitter.cfg_password
    
    _log_to_console("  Password Validation Results:\n")
    result = Transmitter.MetchingData(c_password, t_password, str1, str2)
    
    if result['status'] == 'OK':
        _log_to_console(f"    ✓ Password: Expected '{c_password}' matches Actual '{t_password}'\n")
    else:
        _log_to_console(f"    ✗ Password: Expected '{c_password}' does not match Actual '{t_password}'\n")
    
    _log_to_console(separator + "\n")
    return (result)

def CallJantaraProviderTrxid():
    return (t_respontrxid)

def CallJantaraResponStatus():
    return(t_responstatus)

def _compare_dicts_recursive(expected, actual, path="", differences=None):
    """
    Compare two dictionaries recursively and collect all differences
    Returns list of differences with path and values
    """
    if differences is None:
        differences = []
    
    # Get all keys from both dicts
    all_keys = set(expected.keys()) | set(actual.keys())
    
    for key in all_keys:
        current_path = f"{path}.{key}" if path else key
        expected_val = expected.get(key)
        actual_val = actual.get(key)
        
        if key not in expected:
            differences.append({
                "path": current_path,
                "expected": None,
                "actual": actual_val,
                "message": f"Key '{current_path}' not found in Expected (MongoDB)"
            })
        elif key not in actual:
            differences.append({
                "path": current_path,
                "expected": expected_val,
                "actual": None,
                "message": f"Key '{current_path}' not found in Actual (Telco)"
            })
        elif isinstance(expected_val, dict) and isinstance(actual_val, dict):
            # Recursively compare nested dictionaries
            _compare_dicts_recursive(expected_val, actual_val, current_path, differences)
        elif isinstance(expected_val, list) and isinstance(actual_val, list):
            # Compare lists
            if len(expected_val) != len(actual_val):
                differences.append({
                    "path": current_path,
                    "expected": f"List with {len(expected_val)} items",
                    "actual": f"List with {len(actual_val)} items",
                    "message": f"List length mismatch at '{current_path}': Expected {len(expected_val)} items, Actual {len(actual_val)} items"
                })
            else:
                # Compare each item in list
                for i in range(len(expected_val)):
                    item_path = f"{current_path}[{i}]"
                    if isinstance(expected_val[i], dict) and isinstance(actual_val[i], dict):
                        _compare_dicts_recursive(expected_val[i], actual_val[i], item_path, differences)
                    elif expected_val[i] != actual_val[i]:
                        differences.append({
                            "path": item_path,
                            "expected": expected_val[i],
                            "actual": actual_val[i],
                            "message": f"Value mismatch at '{item_path}': Expected '{expected_val[i]}', Actual '{actual_val[i]}'"
                        })
        elif expected_val != actual_val:
            differences.append({
                "path": current_path,
                "expected": expected_val,
                "actual": actual_val,
                "message": f"Value mismatch at '{current_path}': Expected '{expected_val}', Actual '{actual_val}'"
            })
    
    return differences

def _log_to_console(message):
    """Helper function to write to both stdout and stderr for console visibility"""
    sys.stdout.write(message)
    sys.stderr.write(message)
    sys.stdout.flush()
    sys.stderr.flush()

def _check_ttl_expired(mongo_data):
    """
    Check if TTL expired is 14 days from created_at
    Returns (is_valid, message)
    """
    try:
        created_at = mongo_data.get('created_at')
        ttl_expire = mongo_data.get('ttl_expire')
        
        if not created_at or not ttl_expire:
            return False, "created_at or ttl_expire not found in MongoDB data"
        
        # Parse dates (handle different formats)
        if isinstance(created_at, str):
            # Try to parse ISO format
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                # Try other formats
                created_dt = datetime.strptime(created_at.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            created_dt = created_at
        
        if isinstance(ttl_expire, str):
            try:
                ttl_dt = datetime.fromisoformat(ttl_expire.replace('Z', '+00:00'))
            except:
                ttl_dt = datetime.strptime(ttl_expire.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            ttl_dt = ttl_expire
        
        # Calculate expected TTL (14 days from created_at)
        expected_ttl = created_dt + timedelta(days=14)
        
        # Compare dates (only by date, not time)
        if ttl_dt.date() == expected_ttl.date():
            return True, f"TTL expired date matches: {ttl_dt.date()} (14 days from created_at: {created_dt.date()})"
        else:
            return False, f"TTL expired date mismatch: Expected {expected_ttl.date()} (14 days from created_at: {created_dt.date()}), Actual {ttl_dt.date()}"
    
    except Exception as e:
        return False, f"Error checking TTL expired: {str(e)}"

def CheckSmsSegmentMongoDB():
    """
    Check SMS segment from MongoDB and compare with result telco response
    Returns comparison result with detailed differences per key
    """
    # Use both stdout and stderr to ensure visibility in console
    separator = "=" * 80
    _log_to_console(separator + "\n")
    _log_to_console("[CheckSmsSegmentMongoDB] Starting SMS Segment MongoDB validation...\n")
    _log_to_console(separator + "\n")
    
    str1 = "SMS Segment From MongoDB Expected"
    str2 = "SMS Segment From TelcoReceiver Actual"
    
    validation_results = []
    validation_details = []
    
    # Parse respon status (could be JSON string or already parsed)
    _log_to_console("[Step 1] Parsing TelcoReceiver response...\n")
    try:
        if isinstance(t_responstatus, str):
            # Try to parse as JSON
            telco_response = json.loads(t_responstatus)
            _log_to_console("  → Response is JSON string, parsed successfully\n")
        else:
            telco_response = t_responstatus
            _log_to_console("  → Response is already parsed object\n")
    except (json.JSONDecodeError, TypeError) as e:
        # If not JSON, return error
        _log_to_console(f"  ✗ ERROR: Failed to parse response - {str(e)}\n")
        result = {
            "status": "NOK",
            "message": "Invalid response format from TelcoReceiver"
        }
        return result
    
    # Check if response is array (split message) or single object
    if isinstance(telco_response, list):
        _log_to_console(f"[Step 2] Detected SPLIT message response (array with {len(telco_response)} segments)\n")
        # Normalize telco response to match MongoDB structure
        if len(telco_response) > 0:
            # Get transaction_id from first segment
            transaction_id = str(Transmitter.generatediddash)
            _log_to_console(f"[Step 3] Using transaction_id: {transaction_id}\n")
            
            # Get data from MongoDB
            _log_to_console(f"[Step 4] Fetching data from MongoDB (collection: sms_segments)...\n")
            mongo_data = mg.GetSmsSegment(transaction_id)
            if mongo_data is None:
                _log_to_console(f"  ✗ ERROR: Data not found in MongoDB for transaction_id: {transaction_id}\n")
                result = {
                    "status": "NOK",
                    "message": "Data not found in MongoDB for transaction_id: " + str(transaction_id)
                }
                return result
            _log_to_console(f"  ✓ Data retrieved from MongoDB successfully\n")
            
            # Normalize telco response structure to match MongoDB
            _log_to_console(f"[Step 5] Normalizing TelcoReceiver response structure...\n")
            normalized_telco = {
                "transaction_id": transaction_id,
                "dnis": telco_response[0].get('dnis', ''),
                "total_segments": str(len(telco_response)),
                "segments": []
            }
            
            # Sort telco response by segment_num to ensure correct order
            sorted_telco = sorted(telco_response, key=lambda x: int(x.get('segment_num', 0)))
            
            for segment in sorted_telco:
                normalized_telco["segments"].append({
                    "message_id": segment.get('message_id', ''),
                    "segment_num": segment.get('segment_num', '')
                })
            _log_to_console(f"  → Normalized TelcoReceiver: {len(normalized_telco['segments'])} segments, dnis: {normalized_telco['dnis']}\n")
            
            # Normalize MongoDB structure (remove _id if exists, ensure segments are sorted)
            _log_to_console(f"[Step 6] Normalizing MongoDB data structure...\n")
            normalized_mongo = {
                "transaction_id": mongo_data.get('transaction_id', ''),
                "dnis": mongo_data.get('dnis', ''),
                "total_segments": str(mongo_data.get('total_segments', '')),
                "segments": []
            }
            
            # Sort MongoDB segments by segment_num
            mongo_segments = sorted(mongo_data.get('segments', []), key=lambda x: int(x.get('segment_num', 0)))
            for segment in mongo_segments:
                normalized_mongo["segments"].append({
                    "message_id": segment.get('message_id', ''),
                    "segment_num": segment.get('segment_num', '')
                })
            _log_to_console(f"  → Normalized MongoDB: {len(normalized_mongo['segments'])} segments, dnis: {normalized_mongo['dnis']}\n")
            
            # Check transaction_id
            _log_to_console(f"[Step 7] Starting validation checks...\n")
            if normalized_mongo.get('transaction_id') == normalized_telco.get('transaction_id'):
                validation_results.append(True)
                validation_details.append(f"✓ transaction_id: {normalized_mongo.get('transaction_id')} matches")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ transaction_id: Expected {normalized_mongo.get('transaction_id')}, Actual {normalized_telco.get('transaction_id')}")
            
            # Check dnis
            if normalized_mongo.get('dnis') == normalized_telco.get('dnis'):
                validation_results.append(True)
                validation_details.append(f"✓ dnis: {normalized_mongo.get('dnis')} matches")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ dnis: Expected {normalized_mongo.get('dnis')}, Actual {normalized_telco.get('dnis')}")
            
            # Check total_segments
            if normalized_mongo.get('total_segments') == normalized_telco.get('total_segments'):
                validation_results.append(True)
                validation_details.append(f"✓ total_segments: {normalized_mongo.get('total_segments')} matches")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ total_segments: Expected {normalized_mongo.get('total_segments')}, Actual {normalized_telco.get('total_segments')}")
            
            # Check segments
            mongo_segments_list = normalized_mongo.get('segments', [])
            telco_segments_list = normalized_telco.get('segments', [])
            
            if len(mongo_segments_list) == len(telco_segments_list):
                validation_results.append(True)
                validation_details.append(f"✓ segments count: {len(mongo_segments_list)} matches")
                
                # Check each segment
                for i in range(len(mongo_segments_list)):
                    mongo_seg = mongo_segments_list[i]
                    telco_seg = telco_segments_list[i]
                    
                    # Check segment_num
                    if mongo_seg.get('segment_num') == telco_seg.get('segment_num'):
                        validation_results.append(True)
                        validation_details.append(f"✓ segments[{i}].segment_num: {mongo_seg.get('segment_num')} matches")
                    else:
                        validation_results.append(False)
                        validation_details.append(f"✗ segments[{i}].segment_num: Expected {mongo_seg.get('segment_num')}, Actual {telco_seg.get('segment_num')}")
                    
                    # Check message_id
                    if mongo_seg.get('message_id') == telco_seg.get('message_id'):
                        validation_results.append(True)
                        validation_details.append(f"✓ segments[{i}].message_id: {mongo_seg.get('message_id')} matches")
                    else:
                        validation_results.append(False)
                        validation_details.append(f"✗ segments[{i}].message_id: Expected {mongo_seg.get('message_id')}, Actual {telco_seg.get('message_id')}")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ segments count: Expected {len(mongo_segments_list)}, Actual {len(telco_segments_list)}")
            
            # Check TTL expired (14 days from created_at)
            _log_to_console(f"[Step 8] Checking TTL expiration (14 days from created_at)...\n")
            ttl_valid, ttl_message = _check_ttl_expired(mongo_data)
            validation_results.append(ttl_valid)
            if ttl_valid:
                validation_details.append(f"✓ ttl_expire: {ttl_message}")
            else:
                validation_details.append(f"✗ ttl_expire: {ttl_message}")
            
            # Check created_at exists
            if mongo_data.get('created_at'):
                validation_results.append(True)
                validation_details.append(f"✓ created_at: {mongo_data.get('created_at')} exists")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ created_at: missing or null")
            
            # Check updated_at exists
            if mongo_data.get('updated_at'):
                validation_results.append(True)
                validation_details.append(f"✓ updated_at: {mongo_data.get('updated_at')} exists")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ updated_at: missing or null")
            
            all_valid = all(validation_results)
            
            # Print all validation details
            _log_to_console(f"[Step 9] Validation Summary:\n")
            _log_to_console("  " + "-" * 76 + "\n")
            _log_to_console("  SMS Segment MongoDB Validation Results:\n")
            for detail in validation_details:
                _log_to_console(f"    {detail}\n")
            _log_to_console("  " + "-" * 76 + "\n")
            
            if all_valid:
                _log_to_console(f"  ✓ ALL VALIDATIONS PASSED ({len(validation_results)} checks)\n")
                result = {
                    "status": "OK",
                    "message": "SMS Segment matches between MongoDB and TelcoReceiver",
                    "details": validation_details
                }
            else:
                error_count = len([r for r in validation_results if not r])
                _log_to_console(f"  ✗ VALIDATION FAILED: {error_count} out of {len(validation_results)} checks failed\n")
                result = {
                    "status": "NOK",
                    "message": f"Found {error_count} validation error(s)",
                    "details": validation_details
                }
            _log_to_console("=" * 80 + "\n")
        else:
            _log_to_console(f"  ✗ ERROR: Empty response array from TelcoReceiver\n")
            result = {
                "status": "NOK",
                "message": "Empty response array from TelcoReceiver"
            }
    else:
        # Single message (not split), generate expected data from variables
        _log_to_console(f"[Step 2] Detected SINGLE message response (not split)\n")
        transaction_id = str(Transmitter.generatediddash)
        _log_to_console(f"[Step 3] Using transaction_id: {transaction_id}\n")
        
        # Get message_id from telco response
        _log_to_console(f"[Step 4] Extracting message_id from TelcoReceiver response...\n")
        if isinstance(telco_response, dict):
            message_id = telco_response.get('message_id', '')
        elif isinstance(telco_response, str):
            # Try to parse if it's JSON string
            try:
                parsed = json.loads(telco_response)
                message_id = parsed.get('message_id', '') if isinstance(parsed, dict) else ''
            except:
                message_id = ''
        else:
            message_id = ''
        _log_to_console(f"  → Extracted message_id: {message_id}\n")
        
        # Generate expected data from variables
        _log_to_console(f"[Step 5] Generating expected data from Transmitter variables...\n")
        normalized_mongo = {
            "transaction_id": transaction_id,
            "dnis": Transmitter.quinmsisdn,
            "total_segments": "1",
            "segments": [{
                "message_id": message_id,
                "segment_num": "1"
            }]
        }
        _log_to_console(f"  → Generated expected: dnis={normalized_mongo['dnis']}, message_id={message_id}\n")
        
        # Get data from MongoDB to compare
        _log_to_console(f"[Step 6] Fetching data from MongoDB (collection: sms_segments)...\n")
        mongo_data = mg.GetSmsSegment(transaction_id)
        if mongo_data:
            _log_to_console(f"  ✓ Data retrieved from MongoDB successfully\n")
            # Normalize MongoDB structure for comparison
            _log_to_console(f"[Step 7] Normalizing MongoDB data structure...\n")
            normalized_telco = {
                "transaction_id": mongo_data.get('transaction_id', ''),
                "dnis": mongo_data.get('dnis', ''),
                "total_segments": str(mongo_data.get('total_segments', '')),
                "segments": []
            }
            
            # Sort MongoDB segments by segment_num
            mongo_segments = sorted(mongo_data.get('segments', []), key=lambda x: int(x.get('segment_num', 0)))
            for segment in mongo_segments:
                normalized_telco["segments"].append({
                    "message_id": segment.get('message_id', ''),
                    "segment_num": segment.get('segment_num', '')
                })
            _log_to_console(f"  → Normalized MongoDB: {len(normalized_telco['segments'])} segments, dnis: {normalized_telco['dnis']}\n")
            
            # Check transaction_id
            _log_to_console(f"[Step 8] Starting validation checks...\n")
            if normalized_telco.get('transaction_id') == normalized_mongo.get('transaction_id'):
                validation_results.append(True)
                validation_details.append(f"✓ transaction_id: {normalized_telco.get('transaction_id')} matches")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ transaction_id: Expected {normalized_telco.get('transaction_id')}, Actual {normalized_mongo.get('transaction_id')}")
            
            # Check dnis
            if normalized_telco.get('dnis') == normalized_mongo.get('dnis'):
                validation_results.append(True)
                validation_details.append(f"✓ dnis: {normalized_telco.get('dnis')} matches")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ dnis: Expected {normalized_telco.get('dnis')}, Actual {normalized_mongo.get('dnis')}")
            
            # Check total_segments
            if normalized_telco.get('total_segments') == normalized_mongo.get('total_segments'):
                validation_results.append(True)
                validation_details.append(f"✓ total_segments: {normalized_telco.get('total_segments')} matches")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ total_segments: Expected {normalized_telco.get('total_segments')}, Actual {normalized_mongo.get('total_segments')}")
            
            # Check segments
            mongo_segments_list = normalized_mongo.get('segments', [])
            telco_segments_list = normalized_telco.get('segments', [])
            
            if len(mongo_segments_list) == len(telco_segments_list):
                validation_results.append(True)
                validation_details.append(f"✓ segments count: {len(mongo_segments_list)} matches")
                
                # Check each segment
                for i in range(len(mongo_segments_list)):
                    mongo_seg = mongo_segments_list[i]
                    telco_seg = telco_segments_list[i]
                    
                    # Check segment_num
                    if mongo_seg.get('segment_num') == telco_seg.get('segment_num'):
                        validation_results.append(True)
                        validation_details.append(f"✓ segments[{i}].segment_num: {mongo_seg.get('segment_num')} matches")
                    else:
                        validation_results.append(False)
                        validation_details.append(f"✗ segments[{i}].segment_num: Expected {mongo_seg.get('segment_num')}, Actual {telco_seg.get('segment_num')}")
                    
                    # Check message_id
                    if mongo_seg.get('message_id') == telco_seg.get('message_id'):
                        validation_results.append(True)
                        validation_details.append(f"✓ segments[{i}].message_id: {mongo_seg.get('message_id')} matches")
                    else:
                        validation_results.append(False)
                        validation_details.append(f"✗ segments[{i}].message_id: Expected {mongo_seg.get('message_id')}, Actual {telco_seg.get('message_id')}")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ segments count: Expected {len(mongo_segments_list)}, Actual {len(telco_segments_list)}")
            
            # Check TTL expired (14 days from created_at)
            _log_to_console(f"[Step 9] Checking TTL expiration (14 days from created_at)...\n")
            ttl_valid, ttl_message = _check_ttl_expired(mongo_data)
            validation_results.append(ttl_valid)
            if ttl_valid:
                validation_details.append(f"✓ ttl_expire: {ttl_message}")
            else:
                validation_details.append(f"✗ ttl_expire: {ttl_message}")
            
            # Check created_at exists
            if mongo_data.get('created_at'):
                validation_results.append(True)
                validation_details.append(f"✓ created_at: {mongo_data.get('created_at')} exists")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ created_at: missing or null")
            
            # Check updated_at exists
            if mongo_data.get('updated_at'):
                validation_results.append(True)
                validation_details.append(f"✓ updated_at: {mongo_data.get('updated_at')} exists")
            else:
                validation_results.append(False)
                validation_details.append(f"✗ updated_at: missing or null")
            
            all_valid = all(validation_results)
            
            # Print all validation details
            _log_to_console(f"[Step 10] Validation Summary:\n")
            _log_to_console("  " + "-" * 76 + "\n")
            _log_to_console("  SMS Segment MongoDB Validation Results:\n")
            for detail in validation_details:
                _log_to_console(f"    {detail}\n")
            _log_to_console("  " + "-" * 76 + "\n")
            
            if all_valid:
                _log_to_console(f"  ✓ ALL VALIDATIONS PASSED ({len(validation_results)} checks)\n")
                result = {
                    "status": "OK",
                    "message": "SMS Segment matches between MongoDB and Generated Expected Data",
                    "details": validation_details
                }
            else:
                error_count = len([r for r in validation_results if not r])
                _log_to_console(f"  ✗ VALIDATION FAILED: {error_count} out of {len(validation_results)} checks failed\n")
                result = {
                    "status": "NOK",
                    "message": f"Found {error_count} validation error(s)",
                    "details": validation_details
                }
            _log_to_console("=" * 80 + "\n")
        else:
            _log_to_console(f"  ✗ ERROR: Data not found in MongoDB for transaction_id: {transaction_id}\n")
            result = {
                "status": "NOK",
                "message": "Data not found in MongoDB for transaction_id: " + str(transaction_id)
            }
    
    return result

#end check hit Telco
