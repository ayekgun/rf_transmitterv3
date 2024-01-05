soip_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/TransmitterSOIP/set_default?id='

soip_cfg_name818 = 'transmitter-soip-http-premium818'
soip_cfg_name623 = 'transmitter-soip-http-premium623'
soip_cfg_name247 = 'transmitter-soip-http-premium247'

soip_queue818 = 'jns.transmitter.soip.http.premium.818'
soip_queue623 = 'jns.transmitter.soip.http.premium.623'
soip_queue247 = 'jns.transmitter.soip.http.premium.247'

soip_provider = 'SOIP-HTTP-PREMIUM'
soip_robotname = "transmittersoip"
soip_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('mail_to','mail_host','mail_pass','mail_user','mail_port','mail_auth','mail_start_tls','mail_from','mail_subject','mail_message','activemq_host','provider_host','channel_name','provider_hasdr','activemq_txque','activemq_txack','db_user','db_password','db_table','db_host','db_port','db_name','SUBMIT_UNKNOWN','SUCCESS_RECEIVED','SUCCESS_NOT_RECEIVED','SUCCESS_WITH_ERROR','FAILED_SUBMIT','ERR_EXPIRED','RETRY_TIMEOUT','max_retry','activemq_topic','activemq_topic_host','activemq_notifsender','timeout','agais_application_id','queue_persistency','sleep_after_send','string_splitter','token','encoding','working_hour','username','password','account','secret_key')"
