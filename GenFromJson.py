dic_testcase = ['account', 'time', 'sign', 'phones', 'senderId', 'content', 'smsType']

def CheckValueTelcoAccount():
	str1 = "account From Queue =", quin
	str2 = "account From Queue / Table  =", quot
	result = MetchingData(quinaccount, quoutaccount, str1, str2)
	return(result)


def CheckValueTelcoTime():
	str1 = "time From Queue =", quin
	str2 = "time From Queue / Table  =", quot
	result = MetchingData(quintime, quouttime, str1, str2)
	return(result)


def CheckValueTelcoSign():
	str1 = "sign From Queue =", quin
	str2 = "sign From Queue / Table  =", quot
	result = MetchingData(quinsign, quoutsign, str1, str2)
	return(result)


def CheckValueTelcoPhones():
	str1 = "phones From Queue =", quin
	str2 = "phones From Queue / Table  =", quot
	result = MetchingData(quinphones, quoutphones, str1, str2)
	return(result)


def CheckValueTelcoSenderid():
	str1 = "senderId From Queue =", quin
	str2 = "senderId From Queue / Table  =", quot
	result = MetchingData(quinsenderId, quoutsenderId, str1, str2)
	return(result)


def CheckValueTelcoContent():
	str1 = "content From Queue =", quin
	str2 = "content From Queue / Table  =", quot
	result = MetchingData(quincontent, quoutcontent, str1, str2)
	return(result)


def CheckValueTelcoSmstype():
	str1 = "smsType From Queue =", quin
	str2 = "smsType From Queue / Table  =", quot
	result = MetchingData(quinsmsType, quoutsmsType, str1, str2)
	return(result)


global t_account
global t_time
global t_sign
global t_phones
global t_senderId
global t_content
global t_smsType


t_account = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['account'][0])
t_time = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['time'][0])
t_sign = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['sign'][0])
t_phones = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['phones'][0])
t_senderId = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['senderId'][0])
t_content = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['content'][0])
t_smsType = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['smsType'][0])
