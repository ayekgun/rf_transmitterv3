jantara_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmitterjantara/set_default?id='

jantara_robotname = "transmitterjantara"
jantara_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send','api_key','client_id','is_flash','is_unicode')"

#int05
# jantara_provider = 'JTR05INTL'
# jantara_cfg_name818 = 'transmitter-jtr05intl-818'
# jantara_cfg_name623 = 'transmitter-jtr05intl-623'
# jantara_cfg_name247 = 'transmitter-jtr05intl-247'
# jantara_queue818 = 'jns.transmitter.jtr.05.intl.818'
# jantara_queue623 = 'jns.transmitter.jtr.05.intl.623'
# jantara_queue247 = 'jns.transmitter.jtr.05.intl.247'

#int05
jantara_provider = 'JTR02DOM'
jantara_cfg_name818 = 'transmitter-jtr02dom-818'
jantara_cfg_name623 = 'transmitter-jtr02dom-623'
jantara_cfg_name247 = 'transmitter-jtr02dom-247'
jantara_queue818 = 'jns.transmitter.jtr.02.dom.818'
jantara_queue623 = 'jns.transmitter.jtr.02.dom.623'
jantara_queue247 = 'jns.transmitter.jtr.02.dom.247'

# #int05
# jantara_cfg_name818 = 'transmitter-jtr05intl-818'
# jantara_cfg_name623 = 'transmitter-jtr05intl-623'
# jantara_cfg_name247 = 'transmitter-jtr05intl-247'
# jantara_queue818 = 'jns.transmitter.jtr.05.intl.818'
# jantara_queue623 = 'jns.transmitter.jtr.05.intl.623'
# jantara_queue247 = 'jns.transmitter.jtr.05.intl.247'

jantara_retry_mechanisme = True
jantara_reroute_mechanisme = False
