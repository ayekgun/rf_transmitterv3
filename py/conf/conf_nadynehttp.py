
nadynehttp_urlchangerespon = 'http://192.168.181.52:8071/api_selenium/index.php/Transmitternadynehttp/set_default?id='

nadynehttp_cfg_name818 = 'transmitter-nadyne818'
nadynehttp_cfg_name623 = 'transmitter-nadyne623'
nadynehttp_cfg_name247 = 'transmitter-nadyne247'

nadynehttp_queue818 = 'jns.transmitter.nadyne.regular.818'
nadynehttp_queue623 = 'jns.transmitter.nadyne.regular.623'
nadynehttp_queue247 = 'jns.transmitter.nadyne.regular.247'

nadynehttp_provider = 'NADYNE-REGULAR'
nadynehttp_robotname = "transmitternadynehttp"
nadynehttp_cfglookup = "SELECT  lookup_name,lookup_value FROM jns_config where lookup_type = %s and lookup_name in('activemq_notifsender','activemq_topic','activemq_txack','activemq_txque','appKey','channel_name','ERR_EXPIRED','FAILED_SUBMIT','passwd','password','provider_hasdr','provider_pwd','provider_uid','queue_persistency','timeout','username','sleep_after_send','provider_username','provider_password')"
