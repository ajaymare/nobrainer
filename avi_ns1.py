#!/usr/bin/python


import requests
import json
import time
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def setup_logger():
    LOG_FILE = '/opt/avi/log/ns1dns.log'
    logger = logging.getLogger('NS1-DNS')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILE, 'a')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
    TIMEOUT = 60 # secs

logger = setup_logger()


# CreateOrUpdateRecord Module will take variable as record_info which are automatically retrived from 
# virtual service configuration such as name,domain,fqdn and params are values part on script external
# variables such as external DNS IP, apikey,domain etc.
# CreateOrUpdate function will take the vaiables from record_info and param form the data in json format
# uses request put metho to create DNS A Record in External DNS Server

def CreateOrUpdateRecord(record_info, params):
    logger.info ("Executing create DNS Record api")
    apikey = params.get('apikey')
    #domainName = params.get('domainName') 
    #logger.info ("creating DNS Record with donamin:%s"%domainName)
    ddi_address = params.get('ddi_address')
    ip = record_info.get('f_ip_address', '') or record_info.get('ip_address', '')
    subnet = record_info.get('vip_subnets')
    cname = record_info.get('cname', '')
    logger.info("Subnet:%s"%subnet)
    logger.info ("Creating DNS Record with ip:%s"%ip)
    fqdn = record_info.get('fqdn') 
    name = fqdn.split('.')[0]
    domain = '.'.join(fqdn.split('.')[1:])
    ttl = record_info.get('ttl', 900)
    record_type = record_info.get('type', 'DNS_RECORD_A').split('_')[2]
    
    # REST API payload
    data = {
	    "zone": domain,
	    "domain": name + "." + domain,
	    #"type": ip if record_type == 'A' else cname,
        "type": 'A',
        "ttl": ttl,
	    "answers": [
		    {"answer": [ip]}
		    ]
    }
    logger.info ("Executing DNS Create on Server:%s"%ddi_address)
    # Send request to register the FQDN, failures can be raised and the VS creation will fail
    rsp = requests.put ("https://" + ddi_address +"/v1/zones/" + domain +"/" + name +"." +domain + "/A", data=json.dumps(data),
                        headers={"X-NSONE-Key": apikey, "Content-Type": "application/json",
                                'Accept': 'text/plain'},
                        verify=False)

    logger.info ("Created DNS Record:%s"%rsp.json())

    if not rsp:
        err_str = "ERROR:"
        err_str += "   STATUS: " + str(rsp.status_code)
        err_str += "   RESPONSE: " + rsp.text
        err_str += "   MESSAGE: " + rsp.reason
        raise Exception("Failed to add DNS record with %s"%err_str)
    return

# getDNSRecordRef function will valide the DNS entry before deleting the Entry
# if entry not found it will return no record found
# if entry existes it will return DNS Record Details

def getDNSRecordRef(record_info, params):
    logger.info ("Executing get DNS Record status")
    apikey = params.get('apikey')
    #domainName = params.get('domainName') 
    ddi_address = params.get('ddi_address')
    fqdn = record_info.get('fqdn')
    name = fqdn.split('.')[0]
    domain = '.'.join(fqdn.split('.')[1:])
    logger.info ("finding DNS Record:%s"%fqdn)

    rsp = requests.get("https://" + ddi_address +"/v1/zones/" +domain +"/" + name +"." +domain +"/A",
                        headers={"X-NSONE-Key": apikey, "Content-Type": "application/json",
                                'Accept': 'text/plain'},
                        verify=False)

    if not rsp:
        err_str = "ERROR:"
        err_str += "   STATUS: " + str(rsp.status_code)
        err_str += "   RESPONSE: " + rsp.text
        err_str += "   MESSAGE: " + rsp.reason
        raise Exception("DNS Record not found, failed with %s"%err_str)
    return

# DeleteRecord function will delete the DNS entry for any virtual service as soon use deletes the Virtual service
# Before deleting script will validate if the DNS entry exists or not on the DNS Server.

def DeleteRecord(record_info, params):
    logger.info ("Executing Delete DNS Record")
    apikey = params.get('apikey')
    #domainName = params.get('domainName') 
    ddi_address = params.get('ddi_address')
    ip = record_info.get('f_ip_address', '') or record_info.get('ip_address', '')
    fqdn = record_info.get('fqdn') 
    name = fqdn.split('.')[0]
    domain = '.'.join(fqdn.split('.')[1:])
    cname = record_info.get('cname', '')
    record_type = record_info.get('type', 'DNS_RECORD_A').split('_')[2]
    # Check if DNS record is present
    try:
        dns_record = getDNSRecordRef(record_info, params)
        logger.info ("Finding DNS Record:%s"%dns_record)
    except:
        logger.info ("DNS record was not found")
        return

    type = ip if record_type == 'A' else cname

    rsp = requests.delete("https://" + ddi_address +"/v1/zones/" +domain +"/" + name +"." +domain +"/A",
                        headers={"X-NSONE-Key": apikey, "Content-Type": "application/json",
                                'Accept': 'text/plain'},
                        verify=False)
    logger.info ("Deleted DNS Record:%s"%rsp.json())   

    if not rsp:
        err_str = "ERROR:"
        err_str += "   STATUS: " + str(rsp.status_code)
        err_str += "   RESPONSE: " + rsp.text
        err_str += "   MESSAGE: " + rsp.reason
        raise Exception("Failed to delete DNS record with %s"%err_str)
    return
