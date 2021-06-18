import requests
import json
import pandas as pd 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

token=""
proxy = ""
controller "" 
node_ids = []
node_ui_details = []
jvms=[]
node_ui_info = []
nodes_info=[]


headers= {"Authorization" : token,
           "Accept": "application/json, text/plain, */*"}
r = requests.get(controller + "/controller/rest/applications?output=JSON",headers=headers,verify=False)
applications=json.loads(r.text)

for application in applications:
    r = requests.get(controller + "/controller/rest/applications/{0}/nodes?output=JSON".format(application['id']), headers=headers, verify=False)
    nodes = json.loads(r.text)
    for node in nodes:
        node_ids.append(node['id']) 


for node_id in node_ids:
    r = requests.get(controller+"/controller/restui/nodeUiService/appAgentByNodeId/{0}".format(node_id), headers=headers, verify=False)
    if r.text:
        node_ui_details.append(json.loads(r.text))
    
#node_ui_details=[json.loads(x) for x in node_ui_details if x]


for node_detail in node_ui_details:
    jvm_details={}
    if node_detail['latestVmStartupOptions']:
        for jvm_detail in node_detail['latestVmStartupOptions']:
            if '-Dappdynamics' in jvm_detail:
                jvm_detail=jvm_detail.split("=")
                jvm_details.update({jvm_detail[0]:jvm_detail[1]})
    jvm_details.update({'id':node_detail['id']})
    jvms.append(jvm_details)
    if node_detail['latestEnvironmentVariables']:
        for each in node_detail['latestEnvironmentVariables']:
            if each['name'] == "APPDYNAMICS_DOCKER_ENABLED":
                if each['value'] ==  'true':
                    for each in node_detail['latestEnvironmentVariables']:
                        if each['name'] == "APPDYNAMICS_AGENT_APPLICATION_NAME":
                            print(each['value'])
                            
                       
