
bhramayasa_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/TransmitterBhramayasa/set_default?id='

bhramayasa_cfg_name818 = 'transmitter-bhramayasa818'
bhramayasa_cfg_name623 = 'transmitter-bhramayasa623'
bhramayasa_cfg_name247 = 'transmitter-bhramayasa247'

bhramayasa_queue818 = 'jns.transmitter.bhramayasa.premium.818'
bhramayasa_queue623 = 'jns.transmitter.bhramayasa.premium.623'
bhramayasa_queue247 = 'jns.transmitter.bhramayasa.premium.247'

bhramayasa_provider = 'BHRAMAYASA'
bhramayasa_robotname = "transmitterbhramayasa"
bhramayasa_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send','retry_schedule_time','retry_exception','retry_service_type','max_retry')"

bhramayasa_retry_mechanisme = True
bhramayasa_reroute_mechanisme = False
