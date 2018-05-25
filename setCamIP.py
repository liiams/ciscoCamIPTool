#!/usr/bin/python

#TODO: Add better exception handling for cameras that are unreachable (no route to host) vs. not responding to HTTP.

#This script looks for a matching 'camip.txt' file in the same directory from which it is ran.
#camip.txt should have the following format, per line, excluding brackets:
#<old_ip>,<camera_password>,<new_ip>,<new_subnet_mask>,<new_default_gateway>

#The script will log into each camera and update the IP address settings accordingly.
#At the end it will give you a count of those cameras that succeeded (by virtue of receiging an HTTP 200 and success response) or which
#failed (requests.exception).
#A log file will also be created with details of those that succeeded vs. failed.


#This is a first draft.

import json
import logging
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#early work for setting camera IP settings from python. This is for cameras with a known password that will not be changed.
#Later I will add password updating functionality.

#setup logging
logging.basicConfig(filename="setCamIP.log", level=logging.DEBUG)

def updateSettings(camIP,password,newIP,newSubnetMask,newDefaultGateway):

   cam_login_headers = {'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'User-Agent': 'Mozilla/5.0', 'Accept': 'text/plain, */*; q=0.01', 'Referer': 'http://{0}/login.cs'.format(camIP), 'X-Requested-With': 'XMLHttpRequest', 'Connection': 'keep-alive'}
   login_params = {'action': 'login', 'userName': 'admin', 'password': password,'sesionTemp':''}
   try:
       login = requests.get('https://{0}/System.xml'.format(camIP), headers=cam_login_headers, params=login_params, timeout=5, verify=False)
   except requests.exceptions.RequestException as e:
       print(e)
       logging.error(e)
       return "Fail"
   sessionID = login.headers['sessionId']
   print(sessionID)
   set_ip_headers = {"Accept":"*/*","Referer":"http://{0}/ipaddressing.cs?version=1.0&sessionID={0}&action=get".format(camIP,sessionID),"X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0"}
   set_ip_params = {"version":"1.0","sessionID":sessionID,"action":"set","addressingType":"2","ipVersion":"1","ipAddress":newIP,"subnetMask":newSubnetMask,"defaultGatewayIPAddress":newDefaultGateway,"primaryDNSIPAddress":"","secondaryDNSIPAddress":"","mtu":"1500"}
   try:
       set_ip_request = requests.get('https://{0}/ipaddressing.cs?version=1.0&sessionID={0}&action=get'.format(camIP,sessionID), params=set_ip_params, headers=set_ip_headers, verify=False)
   except requests.exceptions.RequestException as e:
       print(e)
       logging.error(e)
       return "Fail"

   print(set_ip_request.status_code)
   print(set_ip_request.text)
   logging.info(set_ip_request.text)
   return "Success"

with open('camip.txt') as f:
    success_count = 0
    fail_count = 0
    for line in f:
        camIP = line.split(',')[0]
        password = line.split(',')[1]
        newIP = line.split(',')[2]
        newSubnetMask = line.split(',')[3]
        newDefaultGateway = line.split(',')[4].strip()
        print("Ready to hit camera.")
        apply_settings = updateSettings(camIP,password,newIP,newSubnetMask,newDefaultGateway)
        if apply_settings == "Success":
            success_count += 1
        if apply_settings == "Fail":
            fail_count += 1
print("Successfully updated: {0} cameras.".format(success_count))
print("Failed cameras: {0}".format(fail_count))
logging.info("Successfully updated: {0} cameras.".format(success_count))
logging.error("Failed cameras: {0}".format(fail_count))
