import config
import requests
import json
import tweepy as tw
import schedule
import time

from collections import defaultdict

#Fucntion to make API call and get Latest data
def get_data():
	r = requests.get(f'{config.URL}')
	data = r.json()
	return data

#function to save data to a JSON file
def save_data(data):
	with open('lastdata.json','w') as f:
		json.dump(data,f)

#Function to remove some of the objects 
def clean_data(data):

	for d in data:
		del d['countryInfo']
		del d['casesPerOneMillion']
		del d['deathsPerOneMillion']
		del d['updated']

	return data

#Function to create nested dictionaries
def nested_dic(key,lst):
	return {dic[key]:{k:v for k,v in dic.items() if k != key} for dic in lst}

#function to compare data
def compare_data(data):

	with open('lastdata.json') as f:
		last_data = json.load(f)

#convert to nested dictionaries 
	last_data = nested_dic('country',last_data)
	current_data = nested_dic('country',data)

#result variable which will be retured 
	result  = defaultdict(lambda: defaultdict(dict))

#get the interstecion(common keys) of last saved data and current saved data
	for country in last_data.keys() & current_data.keys():
#check which items have changed
		if last_data[country]!=current_data[country]:
#check if the country is in defined country list
			if country in config.countries:
#we only need the changed items , for chnage items calculate diffrence
				for keys in last_data[country].keys() & current_data[country].keys():
					change = current_data[country][keys]-last_data[country][keys]
#if chnage is not 0 then create new tags which gets last value , current value and change
					if change != 0 :
						result[country][keys][f"last_value"] = last_data[country][keys]
						result[country][keys][f"new_value"] = current_data[country][keys]
						result[country][keys][f"change"] = change


	return result

#function to tweet
def tweet(output):

	try:
		auth = tw.OAuthHandler(config.API_key, config.API_secret_key)
		auth.set_access_token(config.Access_token, config.Access_token_secret)
		api = tw.API(auth)
		
	except:
		print("Error:Authnetication Failed")
		return false

	
	api.update_status(output)

#main function wrapped in scheduling job
def job():

	data = get_data()
	
	
	cleandata = clean_data(data)
	
	tweetdata = compare_data(cleandata)

	
	if bool(tweetdata):
		output  = ''
		for country,measures in tweetdata.items():
			output = (f'In {country}\n')
			for measure,values in measures.items():
				output += (f' {measure}  {values["last_value"] } ({"+" if values["change"] > 0 else "" }{values["change"]}) to {values["new_value"]}\n')
			output +='\n'+ config.hashtag	
			print('tweeting',output)		
			tweet((output[:278]+'..') if len(output)>280 else output)		
			save_data(cleandata)
	else:
		print('Nothing to tweet')

#----main------#

job()
schedule.every(2).minutes.do(job)

while 1:
	schedule.run_pending()
	time.sleep(10)