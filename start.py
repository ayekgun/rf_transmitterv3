import sys
from subprocess import call
import os
import pymysql
# import paramiko

transmitter_name = sys.argv[1]
type = sys.argv[2]
pathrobot = 'C:/Python/Python37-32/Scripts/pybot.bat'
#
# transmitter_name = 'jantarav3'
# type = '247'
# pathrobot = 'C:/Python310/Scripts/pybot.bat'

t_robot = 'robot/TransmitterJns'+type+'.robot'
t_robot_e = 'robot/Transmitter'+transmitter_name+type+'.robot'
t_app_name = 'transmitter-jns'+type
#transmitter uniq fitur
t_uniq = 'transmitter-'+transmitter_name+type
user = "root"
passwd = "dockersit123"
host = "192.168.181.52"
db = "test_automation"

ignoretc = {
    "jantarav3": {"TC024*"},
    # "tx_lain": {"TC001*", "TC888888"},
}

# pathrobot = 'C:/Python310/Scripts/pybot.bat'
# dirresult = 'result/'+transmitter_name+'/'+t_uniq
dirresult = 'result/'

def _is_ignored(tc, ignore_patterns):
    """
    Return True kalau 'tc' match salah satu pola di ignore_patterns.
    Pola:
      - Exact (mis. 'TC0231234')
      - Prefix wildcard (mis. 'TC023*')
    Matching case-insensitive.
    """
    if not ignore_patterns:
        return False
    tc_u = (tc or "").upper()
    for pat in ignore_patterns:
        p = (pat or "").upper()
        if not p:
            continue
        if p.endswith("*"):
            if tc_u.startswith(p[:-1]):
                return True
        elif tc_u == p:
            return True
    return False

def GetTestcase():
    array = list()
    con = pymysql.connect(db=db, user=user, passwd=passwd,
                          host=host, port=3306, autocommit=False)
    cur = con.cursor()
    sql = "SELECT testcases FROM test_skenario where status = 1 and app_name in(%s,%s)"
    # sql = "SELECT testcases FROM test_skenario where status = 1 and app_name in(%s,%s) and id in(1)"
    cur.execute(sql, (t_app_name, t_uniq))
    # print(sql, (t_app_name, t_uniq))
    resultDB = cur.fetchall()
    # for row in resultDB:
    #     array.append("-t " + row[0].replace(" ", ""))
    ignore_set = set(ignoretc.get(transmitter_name.lower(), set()))

    for row in resultDB:
        # bersihin spasi dari nilai test case (sesuai logic kamu sebelumnya)
        tc = (row[0] or "").replace(" ", "")
        if not tc:
            continue
        # Skip kalau ada di ignore
        if _is_ignored(tc, ignore_set):
            # print(f"[SKIP] {tc} utk transmitter {transmitter_name}")
            continue
        array.append("-t " + tc)
    return array

if __name__ == '__main__':
    testcase = GetTestcase()
    transmitter_name = 'TransmitterName:'+transmitter_name
    if len(testcase)  != 0:
        # list = [pathrobot, '-t TC021-1 key match Sender Kosong', '-v',transmitter_name,  '-d', dirresult]
        list = [pathrobot, '-v',transmitter_name,  '-d', dirresult]
        for row in testcase:
            list.append(row)
        list.append(t_robot)
        print(list)
        call(list)
        # UploadResult()zz
    else:
        print('TestCaseNotFound')
        pass
