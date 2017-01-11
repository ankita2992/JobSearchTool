import indeedScraper as IS
import jobGatewayScraper as GS
import csv
import pprint

# Walk B to find all jobs in A that are not in B, given
# that they have the same ordering
def jobDifference(jobsA, jobsB):
    result = []
    index = 0
    for job in jobsB:
        while index + 1 < len(jobsA) and jobsA[index] != job:
            result += [jobsA[index]]
            index = index + 1
        index = index + 1
    return result

# finding jobs which do not salary information
# Only for JobGateway, since indeed estimates salaries.
def getUnsalariedJobs(what, where, count, jobType, radius):
    allJobs = GS.getRawJobs(what, where, count, jobType, radius, "0")
    salariedJobs = GS.getRawJobs(what, where, count, jobType, radius, "1")

    # jobs which are in salariedJobs but not allJobs are notSalaried
    return jobDifference(allJobs, salariedJobs)

# Fields Received for getJobs
#   company
#   jobtitle
#   url
#   snippet
#   formattedLocationFull
#   formattedRelativeTime
def getJobs(what, where, count, salaryRanges, jobType = "", radius = 25):
# salaryBrackets must be strictly increasing

    jobs = []
    jobs += [[getUnsalariedJobs(what, where, count, jobType, radius), "Unsalaried", "Unsalaried"]]
    
    # Use 1 as salary to remove unsalaried jobs from query results
    minSal = "1"

    # Since the ordering of the jobs are maintained across different salaries,
    # we use differences in salary queries to find jobs within ranges
    prevIndeedJobs = IS.getRawJobs(what, where, count, jobType, radius, minSal)
    prevGatewayJobs = GS.getRawJobs(what, where, count, jobType, radius, minSal)
    for maxSal in salaryRanges:
        indeedJobs = IS.getRawJobs(what, where, count, jobType, radius, maxSal)
        gatewayJobs = GS.getRawJobs(what, where, count, jobType, radius, maxSal)
        rangedJobs = jobDifference(prevIndeedJobs, indeedJobs) + jobDifference(prevGatewayJobs, gatewayJobs)

        jobs += [[rangedJobs, minSal, maxSal]]

        prevIndeedJobs = indeedJobs
        prevGatewayJobs = gatewayJobs
        minSal = maxSal

    jobs += [[prevIndeedJobs + prevGatewayJobs, maxSal, "Unbounded"]]
    return jobs
        
salaryRanges = ["10000", "50000", "100000"]
res = getJobs("Sales", "Pittsburgh", 10, salaryRanges)
pprint.pprint(res)
