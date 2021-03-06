import logging
import deltabot
import config
import os
import praw
import time
import configparser
from flask import Flask, request
import socket
from threading import Thread
#===============Startup Functions============
app = Flask(__name__)

conf = config.Config(os.getcwd() + '/config/config.json')
reddit_client = praw.Reddit(conf.subreddit + ' bot', site_name=conf.site_name,api_request_delay=1)

#Get/set Config information
Config = configparser.ConfigParser()
Config.read('app_info.cfg')
REDIRECT_URI = 'http://'+socket.gethostbyname(socket.gethostname())+':65010/authorize_callback'
CLIENT_ID = Config.get('Reddit App','cid')
CLIENT_SECRET = Config.get('Reddit App','csec')
access_information = ''

#########################################SCOPES#########################################
scope = 'identity wikiedit wikiread edit flair modconfig modflair modposts privatemessages read submit'
#SEE http://praw.readthedocs.org/en/latest/pages/oauth.html#oauth-scopes FOR DETAILS.
########################################################################################

#Function to kill webserver once access is granted
def kill():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	return "Shutting down..."

#Function to receive callback, set access, then kill server
@app.route('/authorize_callback')
def authorized():
	global access_information
	state = request.args.get('state', '')
	code = request.args.get('code', '')
	access_information = reddit_client.get_access_information(code)
	user = reddit_client.get_me()
	text = 'Bot successfully started.'
	kill()
	return text
	
#Continuous loop to refresh access
def refresh_access():
	while(True):
		time.sleep(1740)
		reddit_client.refresh_access_information(access_information['refresh_token'])
#============================================

def sandbox():
    #FOR TESTING. Put whatever here.
    bot = deltabot.DeltaBot()

def main():
	#Config client
	reddit_client.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
	
	#Print access-grant URL
	print('Follow this URL to grant access: ' + reddit_client.get_authorize_url('DifferentUniqueKey',scope,True))
	
	#Start server to receive callback
	app.run(host="0.0.0.0", debug=False, port=65010)
	
	#Run thread to refresh access every 29 minutes (3 times in any given hour)
	amt = Thread(target=refresh_access,args=())
	amt.daemon=True #Daemon, so it shuts down once main thread quits
	amt.start()
	
	bot = deltabot.DeltaBot(conf, reddit_client)
	bot.go()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
    #sandbox()
