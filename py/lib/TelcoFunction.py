import sys
import os
import json
sys.path.append(os.path.abspath("py"))
import Transmitter

sys.path.append(os.path.abspath("py/lib"))
import ResultTelco_tsel
import ResultTelco_xl
import ResultTelco_nadynehttp
import ResultTelco_jantara
import ResultTelco_modifylong
import ResultTelco_mitracomm
import ResultTelco_soip
import SubmitResult 


def CheckVallueSubmitResultProviderTrxidTsel():
    tprovider = Transmitter.d_provider
    libTelco = 'ResultTelco_'+tprovider
    resultTelco = eval(libTelco).t_responetrxid
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        providertrxid = 'jts-' + \
            str(Transmitter.generatediddash).replace('-', '')
    else:
        if (resultTelco != 'FAILED'):
            providertrxid = 'jts-' + \
                str(Transmitter.generatediddash).replace('-', '')
        else:
            providertrxid = re.sub(r'(^.\|)', '', resultTelco)

    str1 = "Provider Trxid Queue IN"
    str2 = "Provider Trxid Queue Submit Result"
    result = Transmitter.MetchingData(
        providertrxid, SubmitResult.qsm_provider_trxid, str1, str2)
    return (result)


def CheckVallueSubmitResultProviderTrxidXL():
    providertrxid = 'jts-'+str(generatediddash)
    str1 = "Provider Trxid Queue IN"
    str2 = "Provider Trxid Queue Submit Result"
    result = Transmitter.MetchingData(
        providertrxid, SubmitResult.qsm_provider_trxid, str1, str2)
    return (result)

def CheckVallueSubmitResultProviderTrxidNadyne():
    tprovider = Transmitter.d_provider
    libTelco = 'ResultTelco_'+tprovider
    resultTelco = eval(libTelco).CallNadyneResponStatus()
    naydne_trxid = ResultTelco_nadynehttp.CallNaydneProviderTrxid()
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        providertrxid = 'jts-' + \
            str(Transmitter.generatediddash).replace('-', '')
    else:
        if (resultTelco != 'DELIVRD'):
            providertrxid = 'jts-' + \
                str(Transmitter.generatediddash).replace('-', '')
        else:
            providertrxid = naydne_trxid

    str1 = "Provider Trxid Queue IN"
    str2 = "Provider Trxid Queue Submit Result"
    result = Transmitter.MetchingData(
        providertrxid, SubmitResult.qsm_provider_trxid, str1, str2)
    return (result)

def CheckVallueSubmitResultProviderTrxidJantara():
    tprovider = Transmitter.d_provider
    libTelco = 'ResultTelco_'+tprovider
    resultTelco = eval(libTelco).CallJantaraResponStatus()
    respon_status = json.loads(resultTelco)
    # jantara_trxid = ResultTelco_jantara.CallJantaraProviderTrxid()
    
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        providertrxid = str(Transmitter.generatediddash).replace('-', '')
    else:
        if (respon_status['ErrorCode'] == 0):
            jantara_trxid = respon_status['Data'][0]['MessageId']
            providertrxid = jantara_trxid            
        else:
            providertrxid = str(Transmitter.generatediddash).replace('-', '')

    str1 = "Provider Trxid Queue IN"
    str2 = "Provider Trxid Queue Submit Result"
    result = Transmitter.MetchingData(
        providertrxid, SubmitResult.qsm_provider_trxid, str1, str2)
    return (result)

def CheckVallueSubmitResultProviderTrxidModify():
    tprovider = Transmitter.d_provider
    libTelco = 'ResultTelco_'+tprovider
    resultTelco = eval(libTelco).CallModifyResponStatus()
    respon_status = json.loads(resultTelco)
    # jantara_trxid = ResultTelco_jantara.CallJantaraProviderTrxid()
    
    if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
        providertrxid = str(Transmitter.generatediddash).replace('-', '')
    else:
        if (respon_status['ErrorCode'] == 0):
            modify_trxid = respon_status['Data'][0]['MessageId']
            providertrxid = modify_trxid            
        else:
            providertrxid = str(Transmitter.generatediddash).replace('-', '')

    str1 = "Provider Trxid Queue IN"
    str2 = "Provider Trxid Queue Submit Result"
    result = Transmitter.MetchingData(
        providertrxid, SubmitResult.qsm_provider_trxid, str1, str2)
    return (result)

def CheckVallueSubmitResultProviderTrxidMitracomm():
    tprovider = Transmitter.d_provider
    libTelco = 'ResultTelco_'+tprovider
    #Curhat , transmitter ini provider trxid buat sendiri secara random, bukan kaya yang biasanya
    #ambil dari message id , jadi pengecekan nya berdasarkan tidak sama trxid saja huftt
    g_sufix = SubmitResult.qsm_provider_trxid.endswith('_1')
    if(g_sufix == True):
        if(Transmitter.CheckFlowToTelco() == 'expired' or Transmitter.CheckFlowToTelco() == 'bypass'):
            providertrxid = str(Transmitter.generatedid).replace('-', '')
            if(SubmitResult.qsm_provider_trxid ==  str(Transmitter.generatedid) or SubmitResult.qsm_provider_trxid ==  str(Transmitter.generatedid)+'_0'):
                providertrxid = 'providerTrxid == trxid NOK'
            else:
                providertrxid = SubmitResult.qsm_provider_trxid
        else:
            respon_status = eval(libTelco).CallMitracommResponStatus()
            respon_trxid = eval(libTelco).CallMitracommResponTrxid()
            if (respon_status == '0' or respon_status == '-1'):            
                if(SubmitResult.qsm_provider_trxid ==  str(Transmitter.generatedid) or SubmitResult.qsm_provider_trxid ==  str(Transmitter.generatedid)+'_0' ):
                    providertrxid = 'providerTrxid == trxid NOK'
                else:
                    providertrxid = respon_trxid            
            else:
                if(SubmitResult.qsm_provider_trxid ==  str(Transmitter.generatedid) or SubmitResult.qsm_provider_trxid ==  str(Transmitter.generatedid)+'_0' ):
                    providertrxid = 'providerTrxid == trxid NOK'
                else:
                    providertrxid = SubmitResult.qsm_provider_trxid
    else:
        providertrxid = "Prefix Tidak standard"
        
    str1 = "Provider Trxid Queue IN"
    str2 = "Provider Trxid Queue Submit Result"
    result = Transmitter.MetchingData(
        providertrxid, SubmitResult.qsm_provider_trxid, str1, str2)
    return (result)