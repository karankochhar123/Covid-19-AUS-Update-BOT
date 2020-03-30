import config
import requests
import json
import deepdiff
import tweepy as tw
import schedule
import time


def get_data(country):
	r = requests.get(f'{config.URL}{country}')
	return  r.json()

def save_data(data):
	with open(r'C:\Users\KaranKochhar\OneDrive - Lionpoint Group\Python projects\Covid19-Updater\lastdata.json','w') as f:
		json.dump(data,f)

def compare_data(data):

	with open('lastdata.json') as f:
		last_data = json.load(f)

	# print(type(last_data))
	# print(type(data))

	# print("new",data)
	# print("old",last_data)

	# del data['countryInfo']
	# del last_data['countryInfo']
	# del data['country']
	# del last_data['country']


	# print("new",data)
	# print("old",last_data)


	# diff =  {k: data[k] - last_data[k] for k in data.keys() & last_data.keys()} 

	# print(diff)

	diff = deepdiff.DeepDiff(last_data, data)
	#print(diff)
	return diff

def tweet(output):

	try:
		auth = tw.OAuthHandler(config.API_key, config.API_secret_key)
		auth.set_access_token(config.Access_token, config.Access_token_secret)
		api = tw.API(auth)
		
	except:
		print("Error:Authnetication Failed")
		return false

	
	api.update_status(output)

def job():

	data = get_data('australia')
	#save_data(data)
	tweetdata = compare_data(data)

	if bool(tweetdata):
		
		#for k,v in tweetdata:
		#pprint.pprint(tweetdata['values_changed'])
		output = ''
		for k,v in tweetdata['values_changed'].items():
			output +=(f"{k[k.find('[')+1:k.find(']')]} has changed from {v['old_value']} to {v['new_value']}")+'\n'

		
		tweet((output[:278]+'..') if len(output)>280 else output)
		print(f'tweeted:{output}')
		save_data(data)
	else:
		print('nothing new to tweet')


#main#

schedule.every(1).minutes.do(job)

while 1:
	schedule.run_pending()
	time.sleep(1)