import socket
from scapy.all import *
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from tkinter import messagebox
import datetime
import time
from os import system

time_to_live = 2;
nbtns_broadcast_address = "255.255.255.255";
nbtns_port = 137;
llmnr_broadcast_address = "224.0.0.252";
llmnr_port = 5355;
hostname = "garbages001x";
from_email_address = '<insert from email address>'
to_email_address = '<insert to email address>'
sendgrid_api_key = '<insert sendgrid api key>'
log_save_path = "<insert log save path>"

system("title " + "Anti-Responder")

while True:
    llmnr_responder_ip = "<blank>";
    nbtns_responder_ip = "<blank>";

    # Send LLMNR Request
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, time_to_live)
    sock.setblocking(0)
    request = LLMNRQuery(id=RandShort(), qd=DNSQR(qname=hostname))
    sock.sendto(bytes(request), (llmnr_broadcast_address, llmnr_port))

    try:
        (ready, ar1, ar2) = select([sock], [], [], 5)
        if len(ready) > 0:
            p = sock.recv(10240)
            llmnr_response = LLMNRResponse(p)
            llmnr_responder_ip = llmnr_response.an.rdata;
    except socket.error as sox:
        logging.error(sox)
        
    # Send NBT-NS Request
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(0)
    request = NBNSQueryRequest(QUESTION_NAME=hostname)
    sock.sendto(bytes(request), (nbtns_broadcast_address, nbtns_port))

    try:
        (ready, ar1, ar2) = select([sock], [], [], 5)
        if len(ready) > 0:
           p = sock.recv(10240)
           response = NBNSQueryResponse(p)
           nbtns_responder_ip = response.NB_ADDRESS
    except socket.error as sox:
        logging.error(sox)

    print(datetime.datetime.now().strftime("%m/%d/%y, %H:%M:%S") + " IP Address: " + str(llmnr_responder_ip) + " responded to llmnr request. IP Address: " + str(nbtns_responder_ip) + " responded to nbtns request\n")


    # Sent Email and Display Pop-up Message
    if llmnr_responder_ip != "<blank>" or nbtns_responder_ip != "<blank>":
    
        # Log to File
        file = open(log_save_path + 'anti_responder_log.txt', 'a');
        file.write(datetime.datetime.now().strftime("%m/%d/%y, %H:%M:%S"))
        file.write(" IP Address: " + llmnr_responder_ip + " responded to llmnr request. IP Address: " + nbtns_responder_ip + " responded to nbtns request\n")
        file.close()
        
        # Send Email
        message = Mail(
            from_email=from_email_address,
            to_emails=to_email_address,
            subject='Anti-Responder Script Triggered',
            html_content='Script is running on ' + socket.gethostbyname(socket.gethostname()) + '<br>llmnr_responder_ip = ' + llmnr_responder_ip + '<br>nbtns_responder_ip = ' + nbtns_responder_ip)
        try:
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)        
            
        # Pop-Up Message
        messagebox.showinfo("Anti-Responder-Script", "IP Address: " + llmnr_responder_ip + " responded to llmnr request. \n\n IP Address: " + nbtns_responder_ip + " responded to nbtns request")
    
    # Wait 3 minutes
    time.sleep(180)
    
    
    
    
    
