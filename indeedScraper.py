# Author: Jichao Sun (jichaos@andrew.cmu.edu) 
# Date: April 26, 2016 

# Setup: pip install indeed
#        pip install requests --upgrade

from bs4 import BeautifulSoup
from indeed import IndeedClient
import pprint
#import threading, urllib2
#import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, re
import urllib,urllib2, re
import json

jichaoID = 278720823964828
client = IndeedClient(publisher = jichaoID)

# If salary is non empty, then the ordering of jobs per query is preserved.
# Thus can use difference between two queries to find jobs in salary range.
# Jobs with no specified salaries are estimated
def getRawJobs(what, where, count, jobType, radius, salary):
    if jobType not in ["fulltime", "parttime", "contract", "internship", "temporary", ""]:
        return []

    results = []

    params = {
        'q' : what+"+$"+salary,  # Job keywords
        'l' : where,             # Location as a string,
        'jt' : jobType,          # Type of job, fulltime parttime contract etc...
        'radius' : radius,       # Radius in miles
        'userip' : '1.2.3.4',    # Dummy should be fine
        'limit' : 25,            # Max 25
        'useragent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)"
        }

    pageNum = 1
    # Requesting a page at a time
    for i in range(1, count, 25):
        # Check if we ran out of results
        params["start"] = i
        pageResults = client.search(**params)
        
        # Check if we ran out of results (same page as before)
        if pageNum != pageResults["pageNumber"]:
            break
        pageNum += 1
        results += pageResults["results"]

    wantedFields = ["company",                # Company Name
                    "jobtitle",               # Title
                    "url",                    # Indeed URL
                    "snippet",                # Short Description
                    "formattedLocationFull",  # Full Location
                    "formattedRelativeTime"]  # Posted # of days ago

    # Extract only wanted fields
    results = [{k: job[k] for k in wantedFields} for job in results]
    rawJobs = json.dumps(results)
	
    return rawJobs

	
	
salaryBaseURL = "http://www.indeed.com/salary?q1="
def getJobSalaries(jobs):
    for j in jobs:
        # Jobs from gateway has a number attached, remove if exists
        originalTitle = j["jobtitle"]
        cleanTitle = [x for x in originalTitle if not x.isdigit()]
        
        # Build a url to request salary of a title and location
        title = urllib.parse.quote_plus(cleanTitle)
        loc = urllib.parse.quote_plus(j["formattedLocationFull"])
        salaryURL = salaryBaseURL + title + "&l1=" + loc

        # Download page, then find and save the salary.
        page = None
        while page == None:
            try:
                page = urllib.request.urlopen(salaryURL)
                soup = BeautifulSoup(page)
                salary = soup.find("span", {"class" : "salary"}).text
                j["salary"] = salary
            except urllib.error.HTTPError:
                print(salaryURL)
            

# def getJobDescriptions(rawJobs):
#     for job in rawJobs:
#         page = urllib2.urlopen(job["url"])
#         soup = BeautifulSoup(page)
#         descHTML = soup.find("span", {"id" : "job_summary"})
#         job["description"] = descHTML
#     return rawJobs

# # Experimental, since sequential is very slow
# def read_url(**kwargs):
#     data = urllib2.urlopen(kwargs["job"]["url"]).read()
#     soup = BeautifulSoup(data)
#     descHTML = soup.find("span", {"id" : "job_summary"})
#     kwargs["job"]["description"] = descHTML
#     print descHTML
    
# def fetch_parallel(rawJobs):
#     threads = [threading.Thread(target = read_url, kwargs = {"job" : job})
#                for job in rawJobs]
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()
#     return rawJobs
