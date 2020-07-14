import requests
import sys
requests.packages.urllib3.disable_warnings()

#global host
host = sys.argv[1]

def web_server_status():
    if url.status_code == 200:
        print ("Webserver is responding")
    else:
        print ("Webserver is not responding")

def url_get_http():
    for i in range (1 , 100):
        if i%2 == 0: 
            global url    
            url = requests.get("http://"+ host +"")
            #print url
            web_server_status() 
            print (url.headers)
        else:
            url = requests.get("http://"+ host +"")
            #print url
            web_server_status()
            print (url.headers)

def url_get_https():
    for i in range (1 , 100):
        if i%2 == 0:  
            global url    
            url = requests.get("https://"+ host +"",verify=False)
            #print url
            web_server_status()
            print (url.headers)
        else:
            url = requests.get("https://"+ host +"",verify=False)            
            web_server_status()
            print (url.headers)


print ("1. Http Get :")
print ("2. Https Get :")

method = input("Select Method :")

if method == 1:
    url_get_http()

if method == 2:
    url_get_https()    
    
