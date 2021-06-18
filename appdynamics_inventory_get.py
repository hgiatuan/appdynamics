import requests
import json
import csv


params = (
    ('action', 'login'),
)

opt_userid = ''
opt_password = ''
opt_account_name = ''
opt_controller_url = ''
payload = {"type":"BEFORE_NOW","durationInMinutes":60}
s = requests.Session()
proxy = {"https": ""}
response = s.get(opt_controller_url+'/controller/auth?action=login', params=params, auth=(opt_userid + '@' + opt_account_name, opt_password),verify=False,proxies=proxy)
session_cookies = s.cookies.values()
cookies = {
    'JSESSIONID': session_cookies[0],
    'X-CSRF-TOKEN': session_cookies[1]
}
headers = {
    'X-CSRF-TOKEN': session_cookies[1],
    'Content-type': 'application/json', 'Accept': '*/*'
}

r = s.get(opt_controller_url+"/controller/rest/applications?output=JSON",params=params, auth=(opt_userid + '@' + opt_account_name, opt_password),verify=False,proxies=proxy)
applications=json.loads(r.text)

for application in applications:
    node_information = s.get(opt_controller_url+"/controller/rest/applications/{0}/nodes?output=JSON".format(application['id']),params=params, auth=(opt_userid + '@' + opt_account_name, opt_password),verify=False,proxies=proxy)
    tier_information = s.get(opt_controller_url+"/controller/rest/applications/{0}/tiers?output=JSON".format(application['id']),params=params, auth=(opt_userid + '@' + opt_account_name, opt_password),verify=False,proxies=proxy)
    nodes = json.loads(node_information.text)
    tiers = json.loads(tier_information.text)
    for node in nodes:
        r = s.get(opt_controller_url+"/controller/restui/nodeUiService/node/{0}".format(node['id']),headers=headers, cookies=cookies,verify=False,proxies=proxy)
        node_detail = json.loads(r.text)
        node_detail['tierName'] = node_detail.pop('applicationComponentName')
        node_detail['tierId'] = node_detail.pop('componentId')
        node_detail['tierInformation'] = node_detail.pop('componentType')
        node_detail['nodeName'] = node_detail.pop('name')
        node_detail['nodeId'] = node_detail.pop('id')
        node_detail['applicationName'] =  application['name']
        node_detail['applicationId'] = application['id']
        node_detail['applicationGuid'] = application['accountGuid']
        node_detail['accountName'] = opt_account_name
        node_detail['controller'] = opt_controller_url
        metaInfo={}
        for each in node_detail['metaInfo']:
            node_detail[each['name']] = each['value']
            metaInfo[each['name']]= each['value']
        node_detail.update(metaInfo)
        node_detail.pop('metaInfo')
        print(json.dumps(node_detail,indent=4,sort_keys=True))
