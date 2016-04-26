from indeed import IndeedClient

jichaoID = 278720823964828
client = IndeedClient(publisher = jichaoID)

def getRawJobs(what, where, count, radius = 25, salary = ""): 
    results = []

    params = {
        'q' : what,              # Job keywords
        'l' : where,             # Location as a string
        'radius' : radius,       # Radius in miles
        'userip' : '1.2.3.4',    # Dummy should be fine
        'salary' : salary,       # Min Salary
        'limit' : 25,            # Max 25
        'useragent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)"
        }

    # Requesting a page at a time
    for i in range(1, count, 25):
        params["start"] = i
        pageResults = client.search(**params)
        results += pageResults["results"]

    wantedFields = ["company",                # Company Name
                    "jobtitle",               # Title
                    "url",                    # Indeed URL
                    "snippet",                # Short Description
                    "formattedLocationFull",  # Full Location
                    "formattedRelativeTime"]  # Posted # of days ago
 
    # Extract only wanted fields
    results = map(lambda x: {k: x[k] for k in wantedFields}, results)

    return list(results)
