
dws_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmitterdws/set_default?id='

dws_cfg_name818 = 'transmitter-dws818'
dws_cfg_name623 = 'transmitter-dws623'
dws_cfg_name247 = 'transmitter-dws247'

dws_queue818 = 'jns.transmitter.dws.reg.818'
dws_queue623 = 'jns.transmitter.dws.reg.623'
dws_queue247 = 'jns.transmitter.dws.reg.247'

dws_provider = 'DWS-REGULAR'
dws_robotname = "transmitterdws"
dws_cfglookup = "SELECT lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('mail_to','mail_host','mail_pass','mail_user','mail_port','mail_auth','mail_start_tls','mail_from','mail_subject','mail_message','activemq_host','provider_host','channel_name','provider_hasdr','activemq_txque','activemq_txack','db_user','db_password','db_table','db_host','db_port','db_name','SUBMIT_UNKNOWN','SUCCESS_RECEIVED','SUCCESS_NOT_RECEIVED','SUCCESS_WITH_ERROR','FAILED_SUBMIT','ERR_EXPIRED','RETRY_TIMEOUT','max_retry','activemq_topic','activemq_topic_host','activemq_notifsender','timeout','activemq_notifsender','agais_application_id','queue_persistency','sleep_after_send','string_splitter','token','encoding','callbackUrl','working_hour','replace_character','retry_schedule_time','retry_exception','retry_service_type')"

dws_retry_mechanisme = True
dws_reroute_mechanisme = False