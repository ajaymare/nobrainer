#!/usr/local/bin/python3

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from avi.sdk.avi_api import ApiSession

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

avi_controller = '10.206.40.60'
avi_username= 'admin'
avi_password = 'AviNetworks123!'

separator = '-'*80

def avi_cloud_uuid(avi_controller, avi_username, avi_password, tenant="admin"):
        print ('Connecting to Avi Controller Cluster:{}'.format(avi_controller))
        print ('Authenticating to Avi Control Cluster,username:{}'.format(avi_username))
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_cloud = api.get('/cloud')
        if avi_cloud.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code))
            return
        cloud = avi_cloud.json()
        if cloud['count'] == 0:
            print "There are no Clouds Configured"
        else:
            print "Number of Clouds Configured:",cloud['count']
        i = 0
        while cloud['count'] > i:
            print (separator)
            print "Cloud UUID:",cloud['results'][i]['uuid']
            cloud_uuid = cloud['results'][i]['uuid']
            network_subnet_list = api.get("/networksubnetlist/?cloud_uuid="+cloud_uuid+'',params={'page_size':999})
            network_subnet_list_new = network_subnet_list.json()
            if network_subnet_list_new['count'] == 0:
                print ("Networks not found......")
            else:   
                print "Total number of Networks:",network_subnet_list_new['count']
                print "Networks found are:",json.dumps(network_subnet_list_new['results'],indent=4)
            i += 1
        print (separator)
avi_cloud_uuid(avi_controller, avi_username, avi_password)