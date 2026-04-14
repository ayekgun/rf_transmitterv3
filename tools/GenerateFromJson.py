from os import close, write
import urllib.parse
import json
q_type = 'Telco'
file_name = 'GenFromJson.py'

q_in = '{"id":"628118864262","message":"test 18/12/2024","productid":"MustikaInfo","trxdate":"20241223101010","trxid":"xtest-01","userid":"xPCU"}'
x = json.loads(q_in)
ls_data = []
for a in x:
    ls_data.append(a)
    print(a)

f = open(file_name, "w")
f.write("dic_testcase = " + str(ls_data))
f.close()

f = open(file_name, "a")
for a in x:
    ls_data.append(a)    
    f.write("\n\ndef CheckValue"+q_type.title()+a.title() + "():\n")
    f.write("\tstr1 = " + '"'+a+' From Queue ="'+ ","+ " quin"+ "\n")
    f.write("\tstr2 = " + '"'+a+' From Queue / Table  ="' + ","+  " quot"+ "\n")
    f.write("\tresult = MetchingData(quin"+a+", quout"+a+", str1, str2)\n")
    f.write("\treturn(result)\n")


f.write("\n\n")
for a in x:
    ls_data.append(a)    
    f.write("global t_"+a+"\n")

f.write("\n\n")

for a in x:
    ls_data.append(a)    
    f.write("t_"+a+" = (urllib.parse.parse_qs(\n")
    f.write("\tjson_data['parameter'], keep_blank_values=True)['"+a+"'][0])\n")

f.close()