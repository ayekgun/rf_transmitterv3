import pymysql
import sys
import os

sys.path.append(os.path.abspath("py/conf"))
from config import *

con = pymysql.connect(db=db, user=user, passwd=passwd, host=host, port=3306, autocommit=False)
cur = con.cursor()
cur.execute("DESCRIBE out_submitresult")
for row in cur.fetchall():
    print(row[0], row[1])
cur.close()
con.close()
