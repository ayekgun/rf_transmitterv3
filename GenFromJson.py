dic_testcase = ['id', 'message', 'productid', 'trxdate', 'trxid', 'userid']

def CheckValueTelcoId():
	str1 = "id From Queue =", quin
	str2 = "id From Queue / Table  =", quot
	result = MetchingData(quinid, quoutid, str1, str2)
	return(result)


def CheckValueTelcoMessage():
	str1 = "message From Queue =", quin
	str2 = "message From Queue / Table  =", quot
	result = MetchingData(quinmessage, quoutmessage, str1, str2)
	return(result)


def CheckValueTelcoProductid():
	str1 = "productid From Queue =", quin
	str2 = "productid From Queue / Table  =", quot
	result = MetchingData(quinproductid, quoutproductid, str1, str2)
	return(result)


def CheckValueTelcoTrxdate():
	str1 = "trxdate From Queue =", quin
	str2 = "trxdate From Queue / Table  =", quot
	result = MetchingData(quintrxdate, quouttrxdate, str1, str2)
	return(result)


def CheckValueTelcoTrxid():
	str1 = "trxid From Queue =", quin
	str2 = "trxid From Queue / Table  =", quot
	result = MetchingData(quintrxid, quouttrxid, str1, str2)
	return(result)


def CheckValueTelcoUserid():
	str1 = "userid From Queue =", quin
	str2 = "userid From Queue / Table  =", quot
	result = MetchingData(quinuserid, quoutuserid, str1, str2)
	return(result)


global t_id
global t_message
global t_productid
global t_trxdate
global t_trxid
global t_userid


t_id = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['id'][0])
t_message = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['message'][0])
t_productid = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['productid'][0])
t_trxdate = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['trxdate'][0])
t_trxid = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['trxid'][0])
t_userid = (urllib.parse.parse_qs(
	json_data['parameter'], keep_blank_values=True)['userid'][0])
