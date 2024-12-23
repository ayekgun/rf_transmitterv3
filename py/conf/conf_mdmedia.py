mdmedia_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/TransmitterMD/set_default?id='

mdmedia_cfg_name818 = 'transmitter-mdmedia-regular818'
mdmedia_cfg_name623 = 'transmitter-mdmedia-regular623'
mdmedia_cfg_name247 = 'transmitter-mdmedia-regular247'

mdmedia_queue818 = 'jns.transmitter.mdmedia.reg.818'
mdmedia_queue623 = 'jns.transmitter.mdmedia.reg.623'
mdmedia_queue247 = 'jns.transmitter.mdmedia.reg.247'

mdmedia_provider = 'MD-MEDIA-REGULAR'
mdmedia_robotname = "transmittermdmedia"
mdmedia_cfglookup = "SELECT lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('mail_to','mail_host','mail_pass','mail_user','mail_port','mail_auth','mail_start_tls','mail_from','mail_subject','mail_message','activemq_host','provider_host','channel_name','provider_hasdr','activemq_txque','activemq_txack','db_user','db_password','db_table','db_host','db_port','db_name','SUBMIT_UNKNOWN','SUCCESS_RECEIVED','SUCCESS_NOT_RECEIVED','SUCCESS_WITH_ERROR','FAILED_SUBMIT','ERR_EXPIRED','RETRY_TIMEOUT','max_retry','activemq_topic','activemq_topic_host','activemq_notifsender','timeout','activemq_notifsender','agais_application_id','queue_persistency','sleep_after_send','string_splitter','token','encoding','callbackUrl','working_hour','replace_character','uid','pwd')"

mdmedia_retry_mechanisme = False