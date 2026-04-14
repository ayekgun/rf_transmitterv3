
tsel_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmittertsel/set_default?id='

tsel_cfg_name818 = 'transmitter-tsel818'
tsel_cfg_name623 = 'transmitter-tsel623'
tsel_cfg_name247 = 'transmitter-tsel247'

tsel_queue818 = 'jns.transmitter.tsel.other.reg.818'
tsel_queue623 = 'jns.transmitter.tsel.other.reg.623'
tsel_queue247 = 'jns.transmitter.tsel.other.reg.247'

tsel_provider = 'TSEL-OTHER-REGULAR'
tsel_robotname = "transmittertsel"
tsel_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send')"
