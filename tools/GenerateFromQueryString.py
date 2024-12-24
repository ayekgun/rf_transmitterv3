from os import close, write
import urllib.parse
import datetime

q_type = 'Mdmedia'
file_name_in = 'GenFromQS_in.txt'
file_name_out = 'GenFromQS_out.txt'

table_out = 'out_drrealpush_jns'

robotname = 'transmittermdmedia'
#keyword yang akan di check
keywordname = 'CheckResultTelco'
import_class = "Transmitter"

q_in = "sender=senderJSON&msisdn=6281202000319&message=Test+Optional+Parameter+Tanpa+uploadby"

x = urllib.parse.parse_qs(q_in , keep_blank_values=True)
ls_data = []
ls_data_out = []

def dicTestCases():
    for a in x:
        ls_data.append("quin"+str(a))
        ls_data_out.append(str(a))
        print(a)
    f = open(file_name_in, "w")
    f.write("dic_testcase = " + str(ls_data))
    f.write("\n\n")
    f.write("dic_testcase_out = " + str(ls_data_out))
    f.close()

def createFungctionCheck():
    f = open(file_name_out, "w")
    for a in x:
        # ls_data.append(a)    
        queuein = import_class+".quin"+a
        queueout = import_class+".quout"+a
        f.write("\n\ndef CheckValue"+a.title()+q_type.title() + "():\n")
        f.write("\tstr1 = " + '"'+a+' From Queue ="'+ ","+ queuein + "\n")
        f.write("\tstr2 = " + '"'+a+' From Queue / Table  ="' + ","+queueout + "\n")
        f.write("\tresult = Transmitter.MatchingData("+queuein+", "+queueout+", str1, str2)\n")
        f.write("\treturn(result)\n")
    f.close()

def createQueryInsert():
    i = 2
    f = open(file_name_out, "a")
    f.write("\ninsert into `config_keyword` (`appname`, `keyword`, `subkeyword`, `step`, `status`, `date`, `description`) values('"+robotname+"','CheckQueue"+keywordname+"','SetVariableQueue"+keywordname+q_type.title()+"','1','1','2023-01-15 00:00:00',NULL);")
    for a in x:
        # ls_data.append(a)    
        f.write("\ninsert into `config_keyword` (`appname`, `keyword`, `subkeyword`, `step`, `status`, `date`, `description`) values('"+robotname+"','CheckQueue"+keywordname+"','CheckValue"+a.title()+q_type.title()+"','"+str(i)+"','1','2023-01-15 00:00:00',NULL);")
        i += 1
    f.write("\n\n")
    f.close()

def createTableTestCase():
    f = open(file_name_in, "a")
    f.write("\n\ncreate table `"+robotname+"`(\n`testcase` varchar (300),")
    for a in x:
        f.write("`"+a+"` varchar (300),\n")
    f.write("`format` text ,\n`description` varchar (300));\n\n")
    f.close()

def createSampleDataTestCase():
    #Membuat Sample Data
    f = open(file_name_out, "a")
    f.write("insert into `"+robotname+"`(`testcase`,")
    #Membuat nama Coloumn
    for a in x:
        if ls_data[-1] == a:
            f.write("`"+a+"`")
        else:
            f.write("`"+a+"`,")
    f.write(") values ('[TC-001]',")
    #Membuat Isi Coloumn
    for a in x:
        if ls_data[-1] == a:
            f.write("'"+urllib.parse.parse_qs(q_in , keep_blank_values=True)[a][0]+"'")
        else:
            f.write("'"+urllib.parse.parse_qs(q_in , keep_blank_values=True)[a][0]+"',")
    f.write(");\n\n")

    #membuat Query Update  coloumn Format
    f.write("update from "+robotname+" set format ='")
    for a in x:
        if ls_data[0] == a:
            f.write('\\"'+a+'="+(quin'+a+')+')
        elif ls_data[-1] == a:
            f.write('\\"&'+a+'="+(quin'+a+')')
        else:
            f.write('\\"&'+a+'="+(quin'+a+')+')
    f.write('"\' where testcase = "[TC-001]"\n\n')
    f.close

def info():
    f = open(file_name_in, "a")
    pos = len(ls_data) + 1
    f.write("queuemessage = eval(result_Db[X]) di Ganti "+str(pos))
    f.close

def createAMQConsumer():    
    f = open(file_name_out, "a")
    for a in x:
        f.write(a+"= (urllib.parse.parse_qs(message , keep_blank_values = True)['"+a+"'][0])\n")
    f.write("\n\n")
    f.close()

def createTableOut():
    f = open(file_name_out, "a")
    f.write("\n\ncreate table `"+table_out+"`(\n")
    for a in x:
        f.write("`"+a+"` varchar (300),\n")
    f.write("`date_inserted` datetime);\n\n")
    f.close()

def createQueryAmq():
    f = open(file_name_out, "a")
    i = 1
    f.write('cur.execute("insert into out_drpush_jns values(')
    for i in range(len(x)):
        f.write("%s,")
        i+=1
    f.write('NOW())", (')
    for a in x:
        if ls_data[-1] == a:
            f.write(a)
        else:
            f.write(a+",")
    f.write("))\n\n")
    f.close()

def createTelcoResult():    
    f = open(file_name_out, "a")
    f.write("#TelcoResult\n")
    for a in x:
        f.write("global t_"+a+"\n")
    f.write("\n\n")
    for a in x:
        f.write('t_'+a+"= (urllib.parse.parse_qs(json_data['parameter'], keep_blank_values=True)['"+a+"'][0])\n")
    f.write("\n\n")
    f.close()


if __name__ == '__main__':
    dicTestCases()
    createFungctionCheck()
    createTableTestCase()
    createSampleDataTestCase()
    createQueryInsert()
    createAMQConsumer()
    createQueryAmq()
    createTableOut()
    info()
    createTelcoResult()