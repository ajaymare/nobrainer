#!/usr/local/bin/python3
############################################################################
#
# AVI CONFIDENTIAL
# __________________
#
# [2013] - [2019] Avi Networks Incorporated
# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property
# of Avi Networks Incorporated and its suppliers, if any. The intellectual
# and technical concepts contained herein are proprietary to Avi Networks
# Incorporated, and its suppliers and are covered by U.S. and Foreign
# Patents, patents in process, and are protected by trade secret or
# copyright law, and other laws. Dissemination of this information or
# reproduction of this material is strictly forbidden unless prior written
# permission is obtained from Avi Networks Incorporated.
###

from __future__ import print_function
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pyVmomi import vim
from threading import Timer
import ssl
import htmllib
import datetime
import time
import smtplib
from avi.sdk.avi_api import ApiSession
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import schedule

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#avi_controller = '22.242.67.121'
#avi_username= ' '
#avi_password = ' '
##send_email = "avi_reporter@absa.africa"
#send_email = "270_UAT@absa.africa"
receive_email = "CoreServices.LoadBalancer@absa.africa"
receive_email = "marea@vmware.com"
smtp_ip = '22.240.20.32'
smtp_port = '25'


# All the Function Defined below perform Api Call to Avi Controller Cluster IP address as per the variables
# Get the Controller Status using REST API Call, if we have only one Controller on Cluster it will display one Controller is active in cluster
# Incase if we have more than one contorller in cluster it will display the status of controller cluster and each Contorller role
def avi_cluster_check(avi_controller, avi_username, avi_password,fh, tenant="admin"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_cluster = api.get('/cluster/runtime')
        if avi_cluster.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code), file=fh)
            return
        cluster = avi_cluster.json()
        print ('--------------------------------------------------',file=fh)
        print ("Number of Controller in cluster:", len(cluster['node_states']),file=fh)
        print ('--------------------------------------------------',file=fh)
        if len(cluster['node_states']) == 1:
            print ("Cluster Status:",(cluster['cluster_state']['state']),file=fh)
            print ("Node name:" ,cluster['node_states'][0]['name'] + "\tNode Role :",cluster['node_states'][0]['role'],file=fh)
            print ('--------------------------------------------------',file=fh)
        i = 0
        print ("Cluster Status:",cluster['cluster_state']['state'],file=fh)
        print ('--------------------------------------------------',file=fh)
        while len(cluster['node_states']) > i:
            print ("Node name:",cluster['node_states'][i]['name'] + "\tNode Role :",cluster['node_states'][i]['role'],file=fh)
            i = i+1
        print ('--------------------------------------------------',file=fh)

# This Function will be used to get Cloud Connector Health Status.
# This is give you the report as Cloud Status,Cloud name and Cloud Type
def avi_cloud_check(avi_controller, avi_username, avi_password,fh, tenant="admin"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant,verify=False)
        avi_cloud = api.get('/cloud-inventory')
        if avi_cloud.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code))
            return
        cloud = avi_cloud.json()
        if cloud['count'] == 0:
            print ("There are no Clouds Configured",file=fh)
        else:
            print ("Number of Clouds Configured:",cloud['count'],file=fh)
        i = 0
        while cloud['count'] > i:
            print ('--------------------------------------------------',file=fh)
            print ("Cloud Status:",cloud['results'][i]['status']['state'],file=fh)
            print ("Cloud Name:",cloud['results'][i]['config']['name'],file=fh)
            print ("Cloud Type:",cloud['results'][i]['config']['vtype'],file=fh)
            i += 1
        print ('--------------------------------------------------',file=fh)

# This Function will be used to get the Status of Service Engines runnign on given Avi Controller
# This will list the number os Service engines Deployed and Status of Each Servie engine.

def avi_se_check(avi_controller, avi_username, avi_password,fh, tenant="*"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_se = api.get('/serviceengine?join_subresources=runtime',tenant="*",params={'page_size':200})
        if avi_se.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code),file=fh)
            return
        se_status = avi_se.json()
        num_of_se = se_status['count']
        i = 0
        if num_of_se == 0:
            print ("No Service Engines Configured",file=fh)
        else:
            print ("Number of Service Engines deployed:",se_status['count'],file=fh)
            print ('--------------------------------------------------',file=fh)
        while num_of_se > i:
            if se_status['results'][i]['se_connected'] == True:
                print ("Service Engine:",se_status['results'][i]['name'] + "\tStatus:",se_status['results'][i]['runtime']['oper_status']['state'],file=fh)
            else:
                print ("Service Engine:",se_status['results'][i]['name'] + "\tStatus:",se_status['results'][i]['runtime']['oper_status']['state'],file=fh)
            i += 1
# This Function will be used to get the Status of GSLB Service status on Avi Controller
# This will list number of GSLB Services Configured and Stauts of GSLB Service
def avi_gslb_check(avi_controller, avi_username, avi_password, fh,tenant="admin"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_gslb = api.get('/gslbservice?join_subresources=runtime')
        if avi_gslb.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code),file=fh)
            return
        gslb = avi_gslb.json()
        if gslb['count'] == 0:
            print ('--------------------------------------------------',file=fh)
            print ("GSLB Service is Not Configured",file=fh)
           #print ('--------------------------------------------------',file=fh)
        else:
            print ('--------------------------------------------------',file=fh)
            print ("Number of GSLB Services Configured",gslb['count'],file=fh)
        i = 0
        while gslb['count'] > i:
            print ('--------------------------------------------------',file=fh)
            if gslb['results'][i]['runtime']['oper_status']['state'] == 'OPER_UNKNOWN':
                print ("GSLB Service:",gslb['results'][i]['name'] + "\tStatus:",gslb['results'][i]['runtime']['oper_status']['state'],file=fh)
            else:
                print ("GSLB Service:",gslb['results'][i]['name'] + "\tStatus:",gslb['results'][i]['runtime']['oper_status']['state'],file=fh)
            i += 1
        print ('--------------------------------------------------',file=fh)

# This function will be used to get HIGH Level Alerts on the Avi Controller Cluster.
# If there are any HIGH Level Alert which will be displayed on the report.
def avi_alert_check(avi_controller, avi_username, avi_password,fh, tenant="*"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_alert = api.get('/alert',tenant="*")
        if avi_alert.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code),file=fh)
            return
        alert = avi_alert.json()
        if alert['count'] == 0:
            print ("Threre are no alerts on the Controller",file=fh)
        else:
            print ("Number of alerts on Controller are:",alert['count'],file=fh)
            print ('--------------------------------------------------',file=fh)
            j = 0
            print ("Below are the HIGH Level Alerts",file=fh)
            while alert['count'] > 0:
                if alert["results"][j]["level"] == 'ALERT_HIGH':
                    print ("-------------------------------------------------",file=fh)
                    print ("Alert Event",alert['results'][j]['events'],file=fh)
                    j += 1
                    if j == alert['count']:
                        break
                else:
                    j += 1
                    if j == alert['count']:
        #                print ("there are no HIGH Level Alerts",file=fh)
                        break

# This Function will be used to get License Details on Avi Controller.
# Number of License files on Avi Controller and Name of the license file,license file type and remaining license vCPUs
def avi_license_check(avi_controller, avi_username, avi_password,fh, tenant="admin"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_license = api.get('/license')
        if avi_license.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code),file=fh)
            return
        license = avi_license.json()
        if len(license['licenses']) == 0:
            print ("-------------------------------------------------",file=fh)
            print ("License File not found",file=fh)
            print ('--------------------------------------------------',file=fh)
        else:
            print ("--------------------------------------------------",file=fh)
            print ("No of License Files found" , len(license['licenses']),file=fh)
            print ('--------------------------------------------------',file=fh)
        i = 0
        while len(license['licenses']) > i:
            print ("License File name:",license['licenses'][i]['license_name'],file=fh)
            print ("License Type:",license['licenses'][i]['tier_type'],file=fh)
            print ("License Type:",license['licenses'][i]['license_type'],file=fh)
            print ("Number of vCPU License Remaining:",license['licenses'][i]['cores'],file=fh)
            print ('--------------------------------------------------',file=fh)
            i += 1

# This function used to get status of Virtual Services Details
# this will list number of Virtual Services Configured on Avi Controller Cluster and Virtual Service Name which status is down

def avi_vs_check(avi_controller, avi_username, avi_password,fh, tenant="*"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        #api = ApiSession.get_session(avi_controller,avi_username,avi_password)
        avi_virtual_service = api.get('/virtualservice?join_subresources=runtime',params={'page_size':999},tenant='*')
        if avi_virtual_service.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code),file=fh)
            return
        virtual_service = avi_virtual_service.json()
        num_of_vs = virtual_service['count']
        if num_of_vs == 0:
            print ("No Virtual Services Configured",file=fh)
        else:
            print ("Number of Virtual Services Configured:",virtual_service['count'],file=fh)
            print ('--------------------------------------------------',file=fh)
            i = 0
        num_of_vs = len(virtual_service['results'])
        while num_of_vs > i:
            if virtual_service['results'][i]['runtime']['oper_status']['state'] == 'OPER_UP':
               if i == num_of_vs:
                   break
               else:
                   i += 1
            else:
                print ("Virtual Services Name:",virtual_service['results'][i]['name'] + "\tStatus:",virtual_service['results'][i]['runtime']['oper_status']['state'],file=fh)
                if i == num_of_vs:
                    break
                else:
                    i += 1
            #else:
            #    print ("Virtual Services Name:",virtual_service['results'][i]['name'] + "\tStatus:",virtual_service['results'][i]['runtime']['oper_status']['state'],file=fh)
            #    if i == num_of_vs:
            #        break
            #    else:
            #        i += 1
        print ('--------------------------------------------------',file=fh)

# This Function will be used to get the Detials of Backup configuration Avi Controller.
# This will list the most recent backups on Controller.

def avi_backup_check(avi_controller, avi_username, avi_password,fh, tenant="admin"):
        api = ApiSession.get_session(avi_controller, avi_username, avi_password, tenant=tenant)
        avi_backup = api.get('/backup')
        if avi_backup.status_code != 200:
            print ('Error! API responded with:{}'.format(api.status_code),file=fh)
            return
        backup = avi_backup.json()
        if backup['count'] == 0:
            print ("There are no backup found",file=fh)
        else:
            print ("Backup files found:",backup['count'],file=fh)
        i = 0
        print ('--------------------------------------------------',file=fh)
        while backup['count'] > i:
            print ("Backup file name:",backup['results'][i]['file_name'],file=fh)
            print ("Backup time:",backup['results'][i]['timestamp'],file=fh)
            i += 1
        print ('--------------------------------------------------',file=fh)

def avi_health():
    with open('report.log', 'w') as fh:
        print ('Hello there,\r\n\r\nHere is the latest Health Report from Avi Controller:{}'.format(avi_controller),file=fh)
        print('\nConnecting to Avi Controller Cluster:{}'.format(avi_controller), file=fh)
        print('\nAuthenticating to Avi Control Cluster,username:{}\n'.format(avi_username), file=fh)

        avi_cluster_check(avi_controller, avi_username, avi_password, fh)
        avi_cloud_check(avi_controller, avi_username, avi_password, fh)
        avi_se_check(avi_controller, avi_username, avi_password, fh)
        avi_gslb_check(avi_controller, avi_username, avi_password, fh)
        avi_alert_check(avi_controller, avi_username, avi_password, fh)
       #avi_license_check(avi_controller, avi_username, avi_password, fh)
        avi_vs_check(avi_controller, avi_username, avi_password, fh)
        avi_backup_check(avi_controller, avi_username, avi_password, fh)

def main(avi_controller):

    avi_health()
    #sender_email = "avi_reporter@absa.africa"
    sender_email = send_email
    #receiver_email = "CoreServices.LoadBalancer@absa.africa"
    #receiver_email = "marea@vmware.com"
    #receiver_email = "addon.mtonga@absa.co.za"
    receiver_email = receive_email
    message = MIMEMultipart()
    message["Subject"] = "[Avi] Morning Check Report for cluster: {}".format(avi_controller)
    message["From"] = sender_email
    message["To"] = receiver_email
    with open('report.log') as fh:
        buf = fh.read()
    message.attach(MIMEText(buf))
    #server = smtplib.SMTP("22.240.20.32", 25)
    server = smtplib.SMTP(smtp_ip, smtp_port)
    print ("Sending Email.....")
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()   

if __name__ == '__main__':
    with open ('controller.json','r') as var_file:
        var_config = var_file.read()
        obj = json.loads(var_config)
    if len(obj['controller']) == 0:
        print (" Not able to read vars....")
    else:
        i = 0
        while len(obj['controller']) > i:
            avi_controller = obj['controller'][i]['avi_controller']  
            avi_username = obj['controller'][i]['avi_username']
            avi_password = obj['controller'][i]['avi_password']
            send_email = obj['controller'][i]['send_email']
            receive_email = obj['controller'][i]['receive_email']
            main(avi_controller)
        i += 1    
