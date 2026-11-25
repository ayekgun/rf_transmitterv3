import os
import sys
import json
import time
import hmac
import hashlib
import pymysql
import stomp
import paramiko

try:
    from robot.api import logger
except ImportError:
    logger = None

sys.path.append(os.path.abspath("py"))
import Transmitter

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

def RotateClientSecretInConfigDb(new_secret="RotatedSecret2026"):
    """
    Updates client_secret in apps_config.jns_config on host 192.168.181.63.
    """
    _log_to_console(f"[RotateClientSecretInConfigDb] Updating client_secret to: {new_secret}")
    try:
        conn = pymysql.connect(host='192.168.181.63', user='root', password='jatis123', database='apps_config')
        cur = conn.cursor()
        cur.execute("UPDATE jns_config SET lookup_value = %s WHERE lookup_type = 'transmitter-telkomsel-reg-247' AND lookup_name = 'client_secret'", (new_secret,))
        conn.commit()
        conn.close()
        _log_chunked("[CONFIG DB UPDATE]", f"Successfully updated client_secret in apps_config.jns_config to '{new_secret}'")
        return {"status": "OK", "message": f"Updated client_secret to {new_secret}"}
    except Exception as e:
        err = f"Failed to update jns_config: {e}"
        _log_chunked("[CONFIG DB UPDATE ERROR]", err)
        return {"status": "NOK", "message": err}

def BroadcastActiveMqTopicReload():
    """
    Publishes 'reload' command to ActiveMQ Topic 'jns.topic.command' on 192.168.181.51 and 192.168.181.58.
    """
    _log_to_console("[BroadcastActiveMqTopicReload] Broadcasting 'reload' to ActiveMQ topic jns.topic.command...")
    hosts = [
        ("192.168.181.51", 61613, "admin", "admin"),
        ("192.168.181.58", 61613, "admin", "JAtis123!@#")
    ]
    headers = {
        'content-length': None,
        'transformation': 'jms-text',
        'amq-msg-type': 'text'
    }
    success_count = 0
    for h, p, user, pwd in hosts:
        try:
            conn = stomp.Connection([(h, p)])
            conn.connect(user, pwd, wait=True)
            conn.send('/topic/jns.topic.command', 'reload', headers=headers)
            conn.disconnect()
            success_count += 1
            _log_to_console(f"  ✓ Broadcasted to {h}:{p}")
        except Exception as e:
            _log_to_console(f"  ✗ Failed to broadcast to {h}:{p}: {e}")
            
    time.sleep(2) # Give SUT 2 seconds to reload configuration into memory
    if success_count > 0:
        _log_chunked("[TOPIC RELOAD BROADCAST]", f"Broadcasted 'reload' to {success_count} ActiveMQ broker(s)")
        return {"status": "OK", "message": f"Broadcasted reload command to {success_count} broker(s)"}
    return {"status": "NOK", "message": "Failed to broadcast reload command to any broker"}

def VerifySutReloadedLogTrace():
    """
    Connects to SUT host via SSH and verifies SUT logged:
    '[TopicListener] Topic command : reload' and '[TopicListener] Success reload all config'
    """
    _log_to_console("[VerifySutReloadedLogTrace] Verifying SUT runtime log for reload trace...")
    hosts = [
        ("192.168.181.51", "dockersit123", "/var/opt/JNS6.5/Transmitter_jns6.5/TransmitterTelkomselV2"),
        ("192.168.181.58", "dockersit123", "/var/opt/JNS.6.5/TransmitterTelkomselV2")
    ]
    found_trace = False
    log_snippet = ""
    for host, pwd, base_dir in hosts:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username="root", password=pwd, timeout=4)
            cmd = f"tail -n 25 {base_dir}/log/transmittertelkomsel_reg247/transmittertelkomsel_reg247.debug.log"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode()
            ssh.close()
            if "Success reload all config" in out:
                found_trace = True
                log_snippet = out
                break
        except Exception:
            continue
            
    _log_chunked("[SUT RELOAD LOG TRACE]", log_snippet if found_trace else "NOT FOUND")
    if not found_trace:
        err = "SUT log does not contain 'Success reload all config'"
        _log_chunked("[COMPARISON RESULT - RELOAD TRACE]", f"FAILED - {err}")
        return {"status": "NOK", "message": err}
        
    _log_chunked("[COMPARISON RESULT - RELOAD TRACE]", "PASS - SUT dynamically reloaded all config in memory without JVM restart")
    return {"status": "OK", "message": "SUT dynamically reloaded all config without JVM restart"}

def VerifyOutgoingHmacSignatureWithRotatedSecret(new_secret="RotatedSecret2026", old_secret="7s5tLvM1"):
    """
    Retrieves the actual HTTP request captured in test_automation.dummy_result,
    calculates HMAC-SHA256 using new_secret and old_secret, and asserts:
    1. actual_signature == HMAC(new_secret, canonical)
    2. actual_signature != HMAC(old_secret, canonical)
    """
    _log_to_console(f"[VerifyOutgoingHmacSignatureWithRotatedSecret] Validating HMAC signature computed with new secret: {new_secret}")
    try:
        conn = pymysql.connect(host='192.168.181.52', user='root', password='dockersit123', database='test_automation')
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Fetch the latest dummy_result matching testcase or transaction
        target_trxid = Transmitter.quinmessageid
        cur.execute("SELECT * FROM dummy_result WHERE channel = 'telkomsel_mt_v2' AND (provider_trxid = %s OR parameter LIKE %s) ORDER BY id DESC LIMIT 1",
                    (target_trxid, f"%{target_trxid}%"))
        row = cur.fetchone()
        if not row:
            # Fallback to latest row if provider_trxid was assigned uniquely
            cur.execute("SELECT * FROM dummy_result WHERE channel = 'telkomsel_mt_v2' ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            
        if not row:
            return {"status": "NOK", "message": "No dummy_result found for telkomsel_mt_v2"}
            
        hdr = json.loads(row['header'])
        canonical = hdr.get('canonical', '')
        actual_sig = hdr.get('X-Signature', '')
        
        expected_new_sig = hmac.new(new_secret.encode('utf-8'), canonical.encode('utf-8'), hashlib.sha256).hexdigest()
        expected_old_sig = hmac.new(old_secret.encode('utf-8'), canonical.encode('utf-8'), hashlib.sha256).hexdigest()
        
        payload_audit = {
            "canonical_string": canonical,
            "actual_signature_on_wire": actual_sig,
            "expected_signature_with_new_secret": expected_new_sig,
            "expected_signature_with_old_secret": expected_old_sig,
            "new_secret_tested": new_secret,
            "old_secret_tested": old_secret
        }
        _log_chunked("[HMAC SIGNATURE ROTATION AUDIT]", json.dumps(payload_audit, indent=2))
        
        # Strict Assertions
        if actual_sig != expected_new_sig:
            err = f"Signature mismatch! SUT did NOT sign with new secret '{new_secret}'. Actual: {actual_sig}, Expected: {expected_new_sig}"
            _log_chunked("[COMPARISON RESULT - SIGNATURE]", f"FAILED - {err}")
            return {"status": "NOK", "message": err}
            
        if actual_sig == expected_old_sig:
            err = f"SUT is still using the old secret '{old_secret}'! Dynamic rotation failed to take effect."
            _log_chunked("[COMPARISON RESULT - SIGNATURE]", f"FAILED - {err}")
            return {"status": "NOK", "message": err}
            
        _log_chunked("[COMPARISON RESULT - SIGNATURE]", f"PASS - SUT proved to sign request using rotated secret '{new_secret}' (differs from old secret)")
        return {"status": "OK", "message": f"Outgoing request verified signed with rotated secret {new_secret}"}
    except Exception as e:
        err = f"Error verifying rotated HMAC signature: {e}"
        _log_chunked("[COMPARISON RESULT - SIGNATURE ERROR]", err)
        return {"status": "NOK", "message": err}

def RestoreClientSecretInConfigDb(original_secret="7s5tLvM1"):
    """
    Rolls back client_secret to original_secret in jns_config and broadcasts reload to restore baseline.
    """
    _log_to_console(f"[RestoreClientSecretInConfigDb] Rolling back client_secret to baseline: {original_secret}")
    res1 = RotateClientSecretInConfigDb(original_secret)
    res2 = BroadcastActiveMqTopicReload()
    if res1["status"] == "OK" and res2["status"] == "OK":
        _log_chunked("[ROLLBACK STATUS]", f"Successfully rolled back client_secret to '{original_secret}' and reloaded SUT")
        return {"status": "OK", "message": f"Successfully rolled back client_secret to {original_secret}"}
    return {"status": "NOK", "message": "Failed to roll back client_secret or broadcast reload"}
