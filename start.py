import sys
from subprocess import call
import os
import pymysql
# import paramiko

# transmitter_name = sys.argv[1]
# type = sys.argv[2]

transmitter_name = 'mdmedia'
type = '623'

t_robot = 'robot/TransmitterJns'+type+'.robot'
t_robot_e = 'robot/Transmitter'+transmitter_name+type+'.robot'
t_app_name = 'transmitter-jns'+type
#transmitter uniq fitur
t_uniq = 'transmitter-'+transmitter_name+type

user = "root"
passwd = "dockersit123"
host = "192.168.181.52"
db = "test_automation"
pathrobot = 'C:/Python310/Scripts/pybot.bat'
# pathrobot = 'C:/Python310/Scripts/pybot.bat'
# dirresult = 'result/'+transmitter_name+'/'+t_uniq
dirresult = 'result/'


def GetTestcase():
    array = list()
    con = pymysql.connect(db=db, user=user, passwd=passwd,
                          host=host, port=3306, autocommit=False)
    cur = con.cursor()
    sql = "SELECT testcases FROM test_skenario where status = 1 and app_name in(%s,%s)"
    # sql = "SELECT testcases FROM test_skenario where status = 1 and app_name in(%s,%s) and id in(220)"
    cur.execute(sql, (t_app_name, t_uniq))
    # print(sql, (t_app_name, t_uniq))
    resultDB = cur.fetchall()
    for row in resultDB:
        array.append("-t " + row[0].replace(" ", ""))
    return array


# def UploadResult():
#     hostname = '192.168.181.58'
#     password = 'sitjatis123'
#     username = "root"
#     port = 22
#     t = paramiko.SSHClient()
#     t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     t.connect(hostname, port=port, username=username, password=password)
#     listfile = os.listdir(localdir)

#     ftp = t.open_sftp()
#     try:
#         ftp.chdir(path=serverdir)  # Test if remote_path exists
#     except IOError:
#         ftp.mkdir(serverdir)  # Create remote_path

#     for file in listfile:
#         ftp.put(localdir + file, serverdir + file)
#         print('Upload File ' + file + ' to Server')
#     ftp.close()


if __name__ == '__main__':
    testcase = GetTestcase()
    transmitter_name = 'TransmitterName:'+transmitter_name
    if len(testcase)  != 0:
        list = [pathrobot, '-v',transmitter_name,  '-d', dirresult]
        for row in testcase:
            list.append(row)
        list.append(t_robot)
        # print(list)
        call(list)
        # UploadResult()
    else:
        print('TestCaseNotFound')
        pass
