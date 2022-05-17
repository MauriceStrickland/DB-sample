#!/usr/bin/env python3
# File name: mail_detection.py
# Description: Checks an Exchange mailbox for messages and parses them for
#   specific details. Then sends them to an API to store in a DB
# Author: Maurice Strickland
# Date: 2022-05-16

import os
import base64
import re
import requests
from exchangelib import Account, Configuration, Credentials, DELEGATE, ItemAttachment, Message, CalendarItem, HTMLBody


def getCredentials():
    """Get credentials from the environment variables"""   
    username = os.environ.get('USER')
    decodedBytes = base64.b64decode(os.environ.get('PWD'))
    decodedStr = str(decodedBytes.decode('utf-8'))
    password = decodedStr

    return username, password

def connect(server, email, username, password):
    """Get Exchange account connection with server"""
    creds = Credentials(username=username, password=password)
    config = Configuration(server=server, credentials=creds)
    return Account(primary_smtp_address=email, autodiscover=False, config = config, access_type=DELEGATE)


def getSuccess(emails):
    '''Validates the email is the type we are looking for'''
    for email in emails:
        subject = email.subject.lower().replace('re: ', '').replace('fw: ', '')
        if "prod: change number" in subject:
            parseSuccessString(email.body)
            email.move_to_trash()
            
    
def parseSuccessString(message):
    '''Parses the email to pull out key details for the database'''
    changePattern = '[a-zA-Z]{2,3}-\d*'
    timePattern = '\d*:\d*\s[A,P,M].'
    datePattern = '\d./\d./\d.'

    #get change number - CO-123456
    match = re.search(changePattern, message)
    changeNumber = match.group(0)   
    #get time - 06:12 PM
    match = re.search(timePattern, message)
    time = match.group(0)
    #get date - 05/16/22
    match = re.search(datePattern, message)
    date = match.group(0)

    saveSuccessRecord(changeNumber,time,date)


def saveSuccessRecord(cn,time,date):
    '''Send the data gather to an REST API to store the data for reporting and visualization'''
    #call to api to store record
    url ='https://website.com/success'
    body = {'changenumber':cn,'date':date,'time':time}
    header = {'Content-Type': 'application/x-www-form-urlencoded'}

    #ignore self-signged cert
    resp = requests.post(url,data=body,headers=header, verify=False)

    #Handle errors from API
    if not resp.ok:
        print(f"Error: Saving {cn}")
    

def get_recent_emails(account, folder_name, count):
    """Retrieves "count" number of emails for a given folder"""
    # Get the folder object
    folder = account.root / 'Top of Information Store' / folder_name

    # Get emails
    return folder.all().order_by('-datetime_received')[:count]


def emailLogin():
    '''Login to the exchange server. Returns an "account" object used
    to interact with the exchange server'''
    server = 'mail.website.com'
    email = 'user@exchange.com'
  

    username, password = getCredentials()
    account = connect(server, email, username, password)

    return account

def main():
    # Connection details
    account = emailLogin()

    print ('Connected')
   
    emails = get_recent_emails(account, 'Success', 1000)
    
    getSuccess(emails)

    
if __name__ == '__main__':
    main()