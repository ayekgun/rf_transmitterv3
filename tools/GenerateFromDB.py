from os import close, write
import pymysql
q_type = 'transmitter-mustika-regular247'
q_lookup = 'transmitter-mustika-regular247'

robotname = 'transmittermustika'
keywordname = 'DrRealPush'

file_name = 'GenFromDBMysql.txt'
db = 'broadcast'
db_lookup = 'apps_config'
user = 'root'
passwd = 'jatis123'
host = '192.168.181.63'
import_class = "DrHandler"

def dicTestCases():
    con = pymysql.connect(db=db, user=user, passwd=passwd,
                            host=host, port=3306, autocommit=False)
    cur = con.cursor()
    cur.execute("SHOW COLUMNS FROM dr_real_backup")
    x = cur.fetchall()
    cur.close()

    ls_data = []
    for a in x:
        ls_data.append(a[0])
        print(a[0])
    f = open(file_name, "w")
    f.write("dic_testcase = " + str(ls_data))
    f.close()

    f = open(file_name, "a")
    for a in x:
        ls_data.append(a[0])
        queuein = import_class+".quin"+a[0]
        queueout = import_class+".quout"+a[0]
        f.write("\n\ndef CheckValue"+q_type.title()+a[0].title() + "():\n")
        f.write("\tstr1 = " + '"'+a[0]+' From Queue ="'+ ","+ queuein + "\n")
        f.write("\tstr2 = " + '"'+a[0]+' From Queue / Table  ="' + ","+queueout+ "\n")
        f.write("\tresult = ck.MatchingData("+queuein+", "+queueout+", str1, str2)\n")
        f.write("\treturn(result)\n\n")
    f.write("\n\n\n")
    f.close()
    #Query Insert
    i = 2
    f = open(file_name, "a")
    f.write("\ninsert into `config_keyword` (`appname`, `keyword`, `subkeyword`, `step`, `status`, `date`, `description`) values('"+robotname+"','CheckQueue"+keywordname+"','SetVariableQueue"+keywordname+"','1','1','2023-01-15 00:00:00',NULL);")
    for a in x:
        # ls_data.append(a)    
        f.write("\ninsert into `config_keyword` (`appname`, `keyword`, `subkeyword`, `step`, `status`, `date`, `description`) values('"+robotname+"','CheckQueue"+keywordname+"','CheckValue"+q_type.title()+a[0].title() +"','"+str(i)+"','1','2023-01-15 00:00:00',NULL);")
        i += 1
    f.write("\n\n")
    f.close()

def QueryLookup():
    con = pymysql.connect(db=db_lookup, user=user, passwd=passwd,
                            host=host, port=3306, autocommit=False)
    cur = con.cursor()
    cur.execute("select lookup_name FROM jns_config where lookup_type = %s ",(q_lookup))
    x = cur.fetchall()
    cur.close()

    f = open(file_name, "a")
    for a in x:
        if a[0] == x[-1][0]:
            f.write("'"+a[0]+"'")
        else:
            f.write("'"+a[0]+"',")
    f.close()


if __name__ == '__main__':
    # dicTestCases()
    QueryLookup()