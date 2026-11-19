import sys
from subprocess import call
import os
import shutil
import pymysql
# import paramiko

# Parse optional site mode flag from arguments
site_mode_arg = os.environ.get('SITE_MODE', 'auto')
for arg in list(sys.argv):
    arg_lower = arg.lower().strip()
    if arg_lower in ('--one-site', '--onesite', '--single-site', '--singlesite', '--single', '-s', '--legacy', '-1'):
        site_mode_arg = 'one_site'
        os.environ['SITE_MODE'] = 'one_site'
        print("[start.py] Configured SITE_MODE: one_site (legacy / single-site mode)")
        sys.argv.remove(arg)
    elif arg_lower in ('--dual-site', '--dualsite', '--dual', '-d', '--two-site', '--twosite', '-2'):
        site_mode_arg = 'dual_site'
        os.environ['SITE_MODE'] = 'dual_site'
        print("[start.py] Configured SITE_MODE: dual_site (v1.3.0 Single DB mode)")
        sys.argv.remove(arg)
    elif arg_lower in ('--auto', '--autodetect'):
        site_mode_arg = 'auto'
        os.environ['SITE_MODE'] = 'auto'
        print("[start.py] Configured SITE_MODE: auto (auto-detect based on MongoDB document)")
        sys.argv.remove(arg)

if len(sys.argv) < 3:
    print("=" * 70)
    print("Transmitter Automation Runner")
    print("=" * 70)
    print("Usage: python start.py <transmitter_name> <type> [testcase_filter] [OPTIONS]")
    print("")
    print("Site Mode Options:")
    print("  --single-site, --single, -s, --legacy : Run in single-site mode (legacy PROD)")
    print("  --dual-site, --dual, -d               : Run in dual-site mode (v1.3.0 Single DB)")
    print("  --auto                                : Auto-detect mode based on MongoDB schema")
    print("")
    print("Examples:")
    print("  python start.py mitracomm 247 --dual-site            # Run all TCs in dual-site mode")
    print("  python start.py mitracomm 247 --single-site          # Run all TCs in legacy/single-site mode")
    print("  python start.py mitracomm 247 TC028 --dual-site      # Run TC028 dual-site deduplication")
    print("  python start.py mitracomm 247 TC025 --single-site    # Run TC025 legacy single-site retry")
    print("=" * 70)
    sys.exit(1)

transmitter_name = sys.argv[1]
type = sys.argv[2]

# Path robot runner (default Jenkins / Python 3.7)
pathrobot = 'C:/Python/Python37-32/Scripts/pybot.bat'
# pathrobot = 'C:/Python310/Scripts/pybot.bat'

# Fallback otomatis jika path Python 3.7 di atas tidak ditemukan di mesin lokal
if not os.path.exists(pathrobot):
    import shutil
    pathrobot = shutil.which('robot') or shutil.which('pybot') or 'robot'

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
    
    # Check for optional 3rd argument to filter specific Test Case
    if len(sys.argv) > 3:
        target_tc = sys.argv[3]
        testcase = [tc for tc in testcase if target_tc.lower() in tc.lower()]
        print(f"Filtering to run only: {target_tc}")
        
    transmitter_name_param = 'TransmitterName:'+transmitter_name
    site_mode_param = 'SiteMode:' + site_mode_arg
    if len(testcase)  != 0:
        listener_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libraries', 'ExcelReporter.py')
        list = [pathrobot, '--listener', listener_path, '-v', transmitter_name_param, '-v', site_mode_param, '-d', dirresult]
        for row in testcase:
            list.append(row)
        list.append(t_robot)
        print(list)
        call(list)
        # UploadResult()zz
    else:
        print('TestCaseNotFound')
        pass
