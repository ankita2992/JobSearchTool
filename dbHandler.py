# Authors: #		Ankita Sastry (ankitasastry@cmu.edu) #		Priyanka Joshi (joshipriyanka@cmu.edu) # Date: Feb 6, 2017 import csvimport indeedScraper as ISimport jsonimport psycopg2import randomfrom random import randintimport stringimport uuid# Needs participants.csv to be in the same folderdef DB_insertParticipantDetails():		try: 		# Connect to the Heroku Database containing the 'Participant' table		connection = psycopg2.connect("host='' \										dbname='' \										user='' \										password=''");		cur = connection.cursor()				# Query to insert participant data into the database		add_participant_data = "INSERT INTO PARTICIPANT \						(name, participant_id, email_addr, job_loc, job_keywords, job_type, num_job_post) \						VALUES(%s, %s, %s, %s, %s, %s, %s);"				# Open the CSV Excel file with unemployment research participant details		f = open("participants.csv", 'rU')		csv_f = csv.reader(f)				# Iterate through the CSV file to get participant data		rowNum = -1 		for row in csv_f:			rowNum += 1						# skip the first two lines of the input CSV Excel file			if rowNum < 2: 				continue 						# Fetch participant details from the CSV excel sheet				''' Details about the position of data in the CSV Excel				row[2] Name				row[0] Response ID 				row[4] Email				row[10] Job Location				row[11] Job Keywords				row[12] Job Type				row[13] Number of Job Postings  '''			# Make a list of values to be inserted in the database				list = (row[2],row[0],row[4],row[10],row[11],row[12],row[13]) 						# Check whether the Response ID is unique			sql_select = "SELECT name FROM participant WHERE participant_id='" + row[0] + "';"			cur.execute(sql_select)			res = cur.fetchone()						# Insert participant details in the database if Response ID is unique			if(res == None):
				cur.execute(add_participant_data,list)				connection.commit()				print('Successful Insertion')			else:				print('Error: Duplicate Participant ID')			except psycopg2.DatabaseError, e:		if connection:			connection.rollback()		print(e)	finally:		if connection:			connection.close()			def DB_insertJobResults():	try:		# Connect to the Heroku Database containing the 'Participant' table		connection = psycopg2.connect("host='' \										dbname='' \										user='' \										password=''");		cur = connection.cursor()				# Query to insert job search results for the participant		sql_insert = "INSERT INTO JOB_SEARCH_RESULTS \						(job_search_id, participant_id, url, company, location, time_posted, job_title, snippet) \						VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"				# Fetch participant variables from the database		cur.execute('SELECT participant_id, job_keywords, job_loc, num_job_post FROM participant;')		participant = cur.fetchall()				# Run indeed scraper on each participant		for i in range(0,len(participant)):			participant_id = participant[i][0]			job_results = IS.getRawJobs(participant[i][1], participant[i][2], participant[i][3], jobType="", radius=50, salary="10000")			json_jobs = json.loads(job_results)						# Insert jobs for participant			for i in json_jobs:				job_srch_id = str(uuid.uuid4())				jobList = (job_srch_id, participant_id, i['url'], i['company'],						i['formattedLocationFull'], i['formattedRelativeTime'],						i['jobtitle'], i['snippet'])								sql_select_jobs = "SELECT * FROM JOB_SEARCH_RESULTS \									WHERE job_search_id='"+job_srch_id+"' \									AND participant_id='"+participant_id+"';"													cur.execute(sql_select_jobs)				res1 = cur.fetchone()				if(res1 == None):					cur.execute(sql_insert,jobList)					connection.commit()					print('Successful Insertion')				else:					print('Error: Duplicate Job')						except psycopg2.DatabaseError, e:		if connection:			connection.rollback()		print(e)	finally:		if connection:			connection.close()			def main():	DB_insertParticipantDetails()	DB_insertJobResults()	main()