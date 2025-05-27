pintar_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/TransmitterPintar/set_default?id='

pintar_cfg_name818 = 'transmitter-pintar-reg-818'
pintar_cfg_name623 = 'transmitter-pintar-reg-623'
pintar_cfg_name247 = 'transmitter-pintar-reg-247'

pintar_queue818 = 'jns.transmitter.pintar.reg.818'
pintar_queue623 = 'jns.transmitter.pintar.reg.623'
pintar_queue247 = 'jns.transmitter.pintar.reg.247'

pintar_provider = 'PINTAR-REGULAR'
pintar_robotname = "transmitterpintar"
pintar_cfglookup = "SELECT lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_host','activemq_notifsender','activemq_topic','activemq_topic_host','activemq_txack','activemq_txque','agais_application_id','channel_name','db_host','db_name','db_password','db_port','db_table','db_user','ERR_EXPIRED','FAILED_SUBMIT','mail_auth','mail_from','mail_host','mail_message','mail_pass','mail_port','mail_start_tls','mail_subject','mail_to','mail_user','max_retry','provider_hasdr','provider_host','queue_persistency','RETRY_TIMEOUT','sleep_after_send','SUBMIT_UNKNOWN','SUCCESS_NOT_RECEIVED','SUCCESS_RECEIVED','SUCCESS_WITH_ERROR','timeout','username','provider_token','provider_type','encoding','callback_method','callback_url','password')"

pintar_retry_mechanisme = False
pintar_reroute_mechanisme = True