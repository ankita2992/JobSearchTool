# Author: Jichao Sun (jichaos@andrew.cmu.edu) 
# Date: May 16, 2016

# Setup: pip install indeed
#        pip install requests --upgrade

from bs4 import BeautifulSoup
import urlparse
import mechanize
import math
import re
import urllib2

baseURL = "https://www.jobgateway.pa.gov/jponline/JobSeeker/ManageJobSearch/"
url = "https://www.jobgateway.pa.gov/jponline/JobSeeker/ManageJobSearch/FindJobs.aspx"

# Gateway jobs query results' ordere is preserved always.
# If salary is "0", all jobs, including unspec salaried, are returned.
# If salary is "1" or greater, then only jobs with salaries larger than spec'd are returned.
def getRawJobs(what, where, count, jobType, radius, salary):
    # Gateway only has fulltime jobs
    if jobType not in ["", "fulltime"]:
        return []
    
    #print '\n'.join(['%s:%s (%s)' % (c.name,c.value,c.disabled) for c in br.form.controls])
    br = prepFirstRequest(what, where, radius, salary)
    br.submit()

    # Resubmit the form after changing the radius
    fixRadius(br, radius)
    
    # Finding how many results there are in total
    soup = BeautifulSoup(br.response().read())
    s = soup.find("span", {"id" : "MPContent_RecordSummaryLabel"}).text
    numResults = int(re.search(r"of \d+", s).group(0)[3:])

    # Counting number of total iterations
    iterations = math.ceil(numResults / 10.0)
    if count <= numResults:
        iterations = math.ceil(count / 10.0)

    # Decrease by 1 for original request.
    iterations -= 1
    
    # list of jobs to fill, and fill with first page
    jobs = []
    parseJobs(soup, jobs)

    # Keep requesting jobs until we're done.
    while iterations > 0:
        prepNextRequest(br)
        success = False
        while success == False:
            try:
                br.submit()
                success = True
            except urllib2.URLError:
                print "Got an error, try again!"
        soup = BeautifulSoup(br.response().read())
        parseJobs(soup, jobs)
        iterations -= 1

    return jobs

def parseJobs(soup, jobs):
    # Use the id to identify the hyperlin and description (just add job num at end)
    linkStr = "MPContent_SearchResultDataGrid_ParticipantNameHyperLink_"
    descripStr = "MPContent_SearchResultDataGrid_JobDescriptionLabel_"

    # Tags for items are alternating, so get both and check parity later
    # each job has 2 items in either items or altItems. 
    items = soup.find_all("td", "Item_cell", style = "white-space:nowrap;")
    altItems = soup.find_all("td", "AlternatingItem_cell", style = "white-space:nowrap;")

    jobCount = (len(items) + len(altItems)) / 2

    for i in range(0, jobCount):
        if i % 2 == 0:
            location = items[i].text
            date = items[i + 1].text
        else:
            location = altItems[i - 1].text
            date = altItems[i].text

        descrip = soup.find(id = descripStr + str(i)).text
        headers = soup.find(id = linkStr + str(i))
        title = headers.text
        link = baseURL + headers.get("href")

        jobItem = {"company" : "Registered Employer",
                   "jobtitle" : title.encode('utf8'),
                   "url" : link.encode('utf8'),
                   "snippet" : descrip.encode('utf8'),
                   "formattedLocationFull" : location.encode('utf8'),
                   "formattedRelativeTime" : date.encode('utf8')}
        jobs += [jobItem]
            

# Radius must be either 0, 10, 25, or 50
def fixRadius(br, radius):
    if radius <= 10:
        radius = 10
    elif radius <= 25:
        radius = 25
    elif radius <= 50:
        radius = 50
    else:
        print "****************** CANT REQUEST MORE THAN 50 MILES RAIDUS ************************"
        radius = 50

    br.select_form(nr=0)
    br.form["ctl00$MPContent$PlusDropDownList"] = [str(radius)]
    br.submit(id="MPContent_ChangeMatchButton")
        
    
        
# Prepares first post request, need to make it identical to the request a browser would send.
# Thus need to add and remove a bunch of arbitrary controls.
def prepFirstRequest(what, where, radius, salary):
    br = mechanize.Browser()
    br.open(url)

    # The only form is the search form so just index.
    br.select_form(nr=0)
    br.addheaders = [('User-agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7')]
    
    # Adding POST request controls 
    br.form.new_control('hidden', '__EVENTTARGET', {'value': ''})
    br.form.new_control('hidden', '__EVENTARGUMENT', {'value': ''})
    br.form.new_control('hidden', 'ctl00$MPContent$ReportJobPstIdSelectedHidden', {'value': ''})
    br.form.new_control('hidden', 'ctl00$MPContent$xPosHidden', {'value': ''})
    br.form.new_control('hidden', 'ctl00$MPContent$yPosHidden', {'value': ''})
    br.form.new_control('hidden', '__VIEWSTATEGENERATOR', {'value': '8980128E'})
    br.fixup()
    
    # Removing unused POST request controls
    ctrl = br.form.find_control("ctl00$MPContent$KeywordsSearchTipsImageButton")
    br.form.controls.remove(ctrl)
    ctrl = br.form.find_control("ctl00$MPContent$FeaturedJobsCheckBox")
    br.form.controls.remove(ctrl)
    ctrl = br.form.find_control("ctl00$MPContent$WhatIsRegEmployerImageButton")
    br.form.controls.remove(ctrl)
    ctrl = br.form.find_control("ctl00$MPContent$DisplayAdditionalOptionsImage")
    br.form.controls.remove(ctrl)
    ctrl = br.form.find_control("ctl00$MPContent$HideAdditionalOptionsImage")
    br.form.controls.remove(ctrl)
    ctrl = br.form.find_control("ctl00$MPContent$SearchBottomButton")
    br.form.controls.remove(ctrl)

    br.form["ctl00$MPContent$JobKeywordsTextBox"] = what
    br.form["ctl00$MPContent$CityTextBox"] = where
    br.form["ctl00$MPContent$MinimumDesiredSalaryTextBox"] = str(salary)
    br.form["ctl00$MPContent$SalaryRangeDropDownList"] = ["1"]
    
    return br

def prepNextRequest(br):
    br.select_form(nr=0)
    br.set_all_readonly(False)
    br["__EVENTTARGET"] = "ctl00$MPContent$CustomNavigationSearchControl$btnNext"
    br["__EVENTARGUMENT"] = ''
    
    toRemove = ["ctl00$MPContent$KeywordsSearchTipsImageButton",
                "ctl00$MPContent$SearchButton",
                "ctl00$MPContent$FeaturedJobsCheckBox",
                "ctl00$MPContent$WhatIsRegEmployerImageButton",
                "ctl00$MPContent$DisplayAdditionalOptionsImage",
                "ctl00$MPContent$HideAdditionalOptionsImage",
                "ctl00$MPContent$SearchBottomButton",
                "ctl00$MPContent$ChangeMatchButton",
                "ctl00$MPContent$CountyDisplayArrowButton",
                "ctl00$MPContent$CountyHideArrowButton",
                "ctl00$MPContent$CityHideArrowButton",
                "ctl00$MPContent$CityDisplayArrowButton",
                "ctl00$MPContent$JobTitleHideArrowButton",
                "ctl00$MPContent$JobTitleDisplayArrowButton",
                "ctl00$MPContent$SalaryHideArrowButton",
                "ctl00$MPContent$SalaryDisplayArrowButton",
                "ctl00$MPContent$JobTypeHideArrowButton",
                "ctl00$MPContent$JobTypeDisplayArrowButton",
                "ctl00$MPContent$OccupationHideArrowButton",
                "ctl00$MPContent$OccupationDisplayArrowButton",
                "ctl00$MPContent$CompanyHideArrowButton",
                "ctl00$MPContent$CompanyDisplayArrowButton",
                "ctl00$MPContent$SourceHideArrowButton",
                "ctl00$MPContent$SourceDisplayArrowButton",
                "ctl00$MPContent$ShiftHideArrowButton",
                "ctl00$MPContent$ShiftDisplayArrowButton",
                "ctl00$MPContent$MailShareImageButton",
                "ctl00$MPContent$FacebookShareImageButton",
                "ctl00$MPContent$TwitterShareImageButton",
                "ctl00$MPContent$LinkedInShareImageButton",
                "ctl00$MPContent$GooglePlusShareImageButton",
                "ctl00$MPContent$SourceCancelButton",
                "ctl00$MPContent$SourceSaveButton",
                "ctl00$MPContent$CategoryRadioButtonList",
                "ctl00$MPContent$SubmitReportButton"]
    
    for field in toRemove:
        ctrl = br.form.find_control(field)
        br.form.controls.remove(ctrl)
        
    #print '\n'.join(['%s:%s (%s)' % (c.name,c.value,c.disabled) for c in br.form.controls])
        
