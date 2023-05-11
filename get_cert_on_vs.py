#!/usr/local/bin/

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ssl
import datetime
import re
from avi.sdk.avi_api import ApiSession
import ansible_runner
#import ansible-runner from ansible

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

avi_controller = '<IP of AVI Controller>'
avi_username= 'admin'
avi_password = 'Password of Controller'
vs_list = []
oldcertname = "cert-ec" #certificate name

def __main__():

    get_virtualservice_cert(avi_controller, avi_username, avi_password, tenant="*") 

    #Disable SSL warnings
# This Function will be connect to the controller and retrieve all the virtual services under all tenants, if you need to querry a specific tenent please mention tenanat name insted of (*)
def get_virtualservice_cert(avi_controller, avi_username, avi_password, tenant="*"):  
    print ('Authenticating to Avi Control Cluster,username:{}'.format(avi_username))
    api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
    avi_resp  = api.get('/virtualservice')
    if avi_resp.status_code != 200:
        print ('Error! API responded with:{}'.format(api.status_code))
        return
    virtualservice = avi_resp.json()
    vs_index = 0
    vs_count = json.dumps(virtualservice['count'])
    while int(vs_count) >= 1:
         vs_name = (json.dumps(virtualservice['results'][vs_index]['name']))
         try:
            #it will get the SSL_KEY_CERT ref from Virtual Service configuration.
            ssl_ref = json.dumps(virtualservice['results'][vs_index]['ssl_key_and_certificate_refs'])
            ssl_ref = ssl_ref.split("/")[5]
            ssl_ref = ssl_ref.replace('"]' ,"")
            if vs_index == int(vs_count)-1:
              print(vs_list)
              break
            else:
                try:
                    #it will retrive SSL_KEY configuration to the SSL_REF from above
                    ssl_resp = api.get("/sslkeyandcertificate/{}".format(ssl_ref))
                except KeyError:
                    if ssl_resp.status_code != 200:
                        print ('Error! API responded with:{}'.format(api.status_code))
                    return 
                else:
                    cert_name = ssl_resp.json()
                    #look for the certficate name and validate againest match criteia "emcrey.com" using lower case to avoid case sensitivity.
                    match = re.search(oldcertname,cert_name['name'].lower())
                    if match:
                        vs_list.append(vs_name)
                    else:
                        pass    
                vs_index += 1              
         except KeyError:
              #print ("ssl not enabled on virtual service{}".format(vs_name))
              if vs_index == int(vs_count)-1:
                  print("Virtual Service using Old Cert:{}".format(vs_list))
                  return vs_list
                  break
              else:
                vs_index += 1

if __name__ == '__main__':
    __main__()
