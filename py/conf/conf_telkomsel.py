telkomsel_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/TransmittertselMTV2/set_default?id='

telkomsel_cfg_name818 = 'transmitter-telkomsel-reg-818'
telkomsel_cfg_name623 = 'transmitter-telkomsel-reg-623'
telkomsel_cfg_name247 = 'transmitter-telkomsel-reg-247'

telkomsel_queue818 = 'jns.transmitter.telkomsel.reg.818'
telkomsel_queue623 = 'jns.transmitter.telkomsel.reg.623'
telkomsel_queue247 = 'jns.transmitter.telkomsel.reg.247'

telkomsel_provider = 'TELKOMSEL-REGULAR'
telkomsel_robotname = "transmittertelkomsel"
telkomsel_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send','max_retry','RETRY_TIMEOUT')"

telkomsel_retry_mechanisme = False
telkomsel_reroute_mechanisme = False

# Site mode setting for Telkomsel:
# 'one_site' : Telkomsel uses in-queue ActiveMQ retry (does not use MongoDB retry_transmitter).
# In one_site mode, TC028 dual-site MongoDB deduplication check is gracefully skipped.
import os
telkomsel_site_mode = os.environ.get('SITE_MODE', 'one_site')
