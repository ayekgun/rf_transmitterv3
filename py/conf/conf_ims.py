ims_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmitterims/set_default?id='

ims_cfg_name818 = 'transmitter-ims818'
ims_cfg_name623 = 'transmitter-ims623'
ims_cfg_name247 = 'transmitter-ims247'

ims_queue818 = 'jns.transmitter.ims.818'
ims_queue623 = 'jns.transmitter.ims.623'
ims_queue247 = 'jns.transmitter.ims.247'

ims_provider = 'IMS'
ims_robotname = "transmitterims"
ims_cfglookup = "SELECT lookup_name, lookup_value FROM jns_config WHERE lookup_type = %s AND lookup_name IN('activemq_topic','activemq_topic_host','mail_to','activemq_txack','mail_host','mail_pass','mail_user','mail_port','mail_auth','mail_start_tls','mail_from','mail_subject','mail_message','activemq_host','provider_host','channel_name','provider_hasdr','username','activemq_txque','password','db_user','db_password','db_table','db_host','db_port','db_name','SUBMIT_UNKNOWN','SUCCESS_RECEIVED','SUCCESS_NOT_RECEIVED','SUCCESS_WITH_ERROR','FAILED_SUBMIT','RETRY_TIMEOUT','queue_persistency','max_retry','activemq_notifsender','agais_application_id','ERR_EXPIRED','timeout','sleep_after_send')"

ims_retry_mechanisme = False
ims_reroute_mechanisme = False
