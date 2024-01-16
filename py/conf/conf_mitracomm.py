
mitracomm_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmittermitracomm/set_default?id='

mitracomm_cfg_name818 = 'transmitter-mitracomm818'
mitracomm_cfg_name623 = 'transmitter-mitracomm628'
mitracomm_cfg_name247 = 'transmitter-mitracomm247'

mitracomm_queue818 = 'jns.transmitter.mitracomm.premium.818'
mitracomm_queue623 = 'jns.transmitter.mitracomm.premium.623'
mitracomm_queue247 = 'jns.transmitter.mitracomm.premium.247'

mitracomm_provider = 'MITRACOMM-PREMIUM'
mitracomm_robotname = "transmittermitracomm"
mitracomm_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send','retry_schedule_time','retry_exception','retry_service_type','max_retry')"

mitracomm_retry_mechanisme = True