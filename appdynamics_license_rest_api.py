import requests
import json
import pandas as pd
import os
import sys
import time
import datetime
import base64
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

def dict_sweep(input_dict, key):
    if isinstance(input_dict, dict):
        return {k: dict_sweep(v, key) for k, v in input_dict.items() if k != key}
    elif isinstance(input_dict, list):
        return [dict_sweep(element, key) for element in input_dict]
    else:
        return input_dict 

params = (

    ('action', 'login'),

)



opt_user_id = ""
opt_password = ""
opt_account_name = ""
opt_controller_url = ""



try:
    payload = {"type":"BEFORE_NOW","durationInMinutes":60}
    proxy = {"https": ""}
    s = requests.Session()
    response = s.get(opt_controller_url+'/controller/auth?action=login', params=params, auth=(opt_userid + '@' + opt_account_name, opt_password),proxies=proxy,verify=False)
    session_cookies = s.cookies.values()

    cookies = {
        'JSESSIONID': session_cookies[0],
        'X-CSRF-TOKEN': session_cookies[1]
    }

    headers = {
        'X-CSRF-TOKEN': session_cookies[1],
        'Content-type': 'application/json', 'Accept': '*/*'
    }

    data = '{"type":"BEFORE_NOW","durationInMinutes":60}'
    licenses=s.get(opt_controller_url+'/controller/mds/v1/license/rules',params=params, auth=(opt_userid + '@' + opt_account_name, opt_password),proxies=proxy,verify=False)
    licenses=json.loads(licenses.text)
    d=[]
    frame = pd.DataFrame()
    for application_license in licenses:
        response = requests.post(opt_controller_url+'/controller/restui/licenseRule/getApmLicenseRuleDetailViewData/{0}'.format(application_license['id']), headers=headers, cookies=cookies, data=data,proxies=proxy,verify=False)
        license_information= json.loads(response.text)
        license_information['application_name'] =  application_license['name']
        license_information['total_licenses'] = application_license['total_licenses']
        license_information['accountName'] = opt_account_name
        license_information['controller'] = opt_controller_url
        license_information['application_id'] = application_license['id']
        license_information['apmStackGraphViewData']=license_information['nonApmModuleDetailViewData'] + license_information['apmStackGraphViewData'] 
        license_information=dict_sweep(license_information,"graphPoints")
        license_information=dict_sweep(license_information,"licenseProvisioned")
        test=((pd.DataFrame([x for x in license_information['apmStackGraphViewData']]).set_index('licenseModuleType')))
        test[application_license['name']] = test['peakUsage']
        test.pop('peakUsage')
        d.append(test)
    frame = pd.concat(d, join='outer', axis=1).fillna('')
    frame.to_csv("C:\\tmp\\test.csv")
        
    license_summary = requests.post(opt_controller_url+'/controller/restui/licenseRule/getAccountUsageSummary', headers=headers, cookies=cookies, data=data,proxies=proxy,verify=False)
    license_summary = json.loads(license_summary.text)
    license_information['accountName'] = opt_account_name
    license_information['controller'] = opt_controller_url
    print(json.dumps(license_summary))
except Exception as e:
    print(e)
