xl_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmitterxl/set_default?id='

xl_cfg_name818 = 'transmitter-xl818'
xl_cfg_name623 = 'transmitter-xl623'
xl_cfg_name247 = 'transmitter-xl247'

xl_queue818 = 'jns.transmitter.xl.premium.818'
xl_queue623 = 'jns.transmitter.xl.premium.623'
xl_queue247 = 'jns.transmitter.xl.premium.247'

xl_provider = 'XL CMP'
xl_robotname = "transmitterxl"
xl_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send','RETRY_TIMEOUT','retryable_error','retryable_servicetype','max_retry')"
