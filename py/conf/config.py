import uuid

global_name_of_robot = 'transmitterjns'
idproccess = uuid.uuid4().hex[:6].upper()

user = "root"
passwd = "dockersit123"
host = "192.168.181.52"
db = "test_automation"

user_bc = "root"
passwd_bc = "jatis123"
host_bc = "192.168.181.63"
db_bc = "broadcast"

user_cfg = "root"
passwd_cfg = "jatis123"
host_cfg = "192.168.181.63"
db_cfg = "apps_config"

# host_amq ="10.0.7.106"
host_amq ="192.168.181.51"
port_amq = 61613

queuesubmitresult ='jns.app.submitresults'

urlcekresult = 'http://192.168.181.52:8071/api_selenium/index.php/CekResult?id='
urlqueuejsp = 'http://192.168.181.51:8161/admin/xml/queues.jsp'
dic_testcase = ["expected_result", "quintrxid", "quinmessageid", "quinmsisdn", "quinmessage", "quinbatchname", "quinclientid", "quindivisionid", "quinsenderid", "quinuid", "quinpwd", "quincpName", "quinuploadby", "quinapproveby", "quindateupload", "quindateapprove", "quindateinqueue", "quinservicetype",
                "quinproviderid", "quinbillable", "quinjatismessageid", "quinuploadtype", "quinsmspartition", "quinexpiry", "quinsender", "quinchannel_mq_name", "quinpriority", "quinadddata1", "quinadddata2", "quinadddata3", "quinchargecode", "quinsenderids", "quinpriority_header", "quinpersistent", "quinoriginmqname"]
dic_txredirect = ["quottrxid", "quotmessageid", "quotmsisdn", "quotmessage", "quotbatchname", "quotclientid", "quotdivisionid", "quotsenderid", "quotuid", "quotpwd", "quotcpName", "quotuploadby", "quotapproveby", "quotdateupload", "quotdateapprove", "quotdateinqueue", "quotservicetype", "quotproviderid",
                  "quotbillable", "quotjatismessageid", "quotuploadtype", "quotsmspartition", "quotexpiry", "quotsender", "quotchannel_mq_name", "quotpriority", "quotadddata1", "quotadddata2", "quotadddata3", "quotchargecode", "quotsenderids", "quotpriority_header", "quotpersistent", "quotorigin_mq_name"]
dic_queuesm = ["channel_name", "provider_submit_status", "date_hit", "transmitter_submit_status", "date_response", "division_id", "chargecode", "trxid", "client_id", "channel_mq_name",
               "channel_is_direct", "duration", "service_type", "without_dr", "job_id", "mask_name", "provider_id", "provider_trxid", "provider_name", "mask_id", "message_seq", "retry", "priority_header", "persistent"]

mongo_conn = 'mongodb://mongoadmin:mongoadmin@192.168.181.63:27017/admin'
# mongo_db = 'whatsappCore'