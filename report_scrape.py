#!/usr/bin/env python3
# File name: report_scrape.py
# Description: Logs in to OBIEE and downloads a report to disk
# Author: Maurice Strickland
# Date: 2022-05-16

import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def setup(savePath):
    '''Setup for the FireFox webdriver'''
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.helperApps.neverAsk.openFile','application/x-csv, text/csv,text,x-csv,text/plain')
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-csv, text/csv,text,x-csv,text/plain')
    profile.set_preference('media.navigator.permission.disabled', True)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", savePath)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 
    "text/plain,text/x-csv,text/csv,application/vnd.ms-excel,application/csv,application/x-csv,text/csv,text/comma-separated-values,text/x-comma-separated-values,text/tab-separated-values,application/pdf")
    profile.set_preference("browser.helperApps.neverAsk.openFile", 
    "text/plain,text/x-csv,text/csv,application/vnd.ms-excel,application/csv,application/x-csv,text/csv,text/comma-separated-values,text/x-comma-separated-values,text/tab-separated-values,application/pdf")
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
    profile.set_preference("pdfjs.disabled", True)

    profile.update_preferences()

    return profile


def runScrape(savePath):
    '''Main function to scrape the page and initate the report download'''
    profile = setup(savePath)

    caps = DesiredCapabilities.FIREFOX.copy()
    caps["firefox_profile"] = profile.encoded
    caps["marionette"] = True

    browser = webdriver.Firefox(executable_path="/geckodriver",firefox_profile = profile,capabilities = caps)
    url = "https://website/analytics/saw.dll?bieehome"
    browser.get(url)

    #waits
    short_wait = WebDriverWait(browser, 10)
    long_wait = WebDriverWait(browser, 15*60)


    #log in

    username = browser.find_element_by_id("sawlogonuser") #username field
    password = browser.find_element_by_id("sawlogonpwd") #password field'

    username.send_keys(os.environ.get('USER'))
    password.send_keys(os.environ.get('PWD'))
    submitButton = browser.find_element_by_id("idlogon")
    submitButton.click()

    #Report link


    short_wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Staffing - Schedule Time - Direct Access")))
    reportLink = browser.find_element_by_link_text("Staffing - Schedule Time - Direct Access")
    reportLink.click()


    #run report
    short_wait.until(EC.presence_of_element_located((By.NAME, "gobtn")))
    runReportButton = browser.find_element_by_name("gobtn")
    runReportButton.click()


    #Export report
    long_wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Export")))
    export_button = browser.find_element_by_partial_link_text("Export")
    browser.execute_script("arguments[0].click()", export_button)
    time.sleep(10)

    #download CSV
    short_wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Data")))
    data_button = browser.find_element_by_link_text("Data")
    data_button.click()
    print ("Data button clicked")

    time.sleep(10)
    short_wait.until(EC.presence_of_element_located((By.LINK_TEXT, "CSV")))
    csv_button = browser.find_element_by_link_text("CSV")
    csv_button.click()
    print ("Csv Button Clicked")

    time.sleep(10)

    #need to know when download is done
    long_wait.until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(), 'Confirmation')]")))
    print ("Download started")
    time.sleep(10)

    max_polls = 2000
    polls = 0

    while polls < max_polls:
        for file1 in os.listdir(savePath):
            print (file1)
            if file1 == "Staffing - Schedule Time - Direct Access.csv":
                print ('Finished downloading')
                break
        time.sleep(10)
        polls += 1
        break

    time.sleep(5)
    browser.quit()

def main():
    savePath = "/downloads"
    #Ensures file does not already exist
    while not os.path.exists(savePath + "/Staffing - Schedule Time - Direct Access.csv"):
        print ("Running Scrape")
        print (str(datetime.datetime.now()))
        runScrape(savePath)


if __name__ == '__main__':
    main()
