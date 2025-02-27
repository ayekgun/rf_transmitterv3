
m360_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/TransmitterM360/set_default?id='

m360_cfg_name818 = 'transmitter-m360-regular818'
m360_cfg_name623 = 'transmitter-m360-regular623'
m360_cfg_name247 = 'transmitter-m360-regular247'

m360_queue818 = 'jns.transmitter.m360.regular.818'
m360_queue623 = 'jns.transmitter.m360.regular.623'
m360_queue247 = 'jns.transmitter.m360.regular.247'

m360_provider = 'm360-REGULAR'
m360_robotname = "transmitterm360"
m360_cfglookup = "SELECT lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('mail_to','mail_from','mail_subject','mail_message','activemq_host','activemq_username','activemq_password','provider_host','channel_name','provider_hasdr','activemq_txque','activemq_txack','db_user','db_password','db_table','db_tableHoliday','db_host','db_port','db_name','SUCCESS_RECEIVED','FAILED_SUBMIT','ERR_EXPIRED','RETRY_TIMEOUT','max_retry','activemq_topic','activemq_topic_host','activemq_topic_username','activemq_topic_password','activemq_notifsender','timeout','activemq_notifsender','agais_application_id','queue_persistency','sleep_after_send','uid','pwd','token')"

m360_retry_mechanisme = False