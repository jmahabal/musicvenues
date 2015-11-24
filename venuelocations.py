# Getting Venue Locations in a City Using the Songkick API

### import and initialize stuff ###

import json
import urllib2
import unicodedata
import requests
import requests_cache
from unidecode import unidecode
import sys

requests_cache.install_cache('demo_cache')

class Venue:

	def __init__(self, id):
		self.listofartists = []
		self.venueid = id

		# boston area id = 18842
		# O2 Academy Brixton id = 17522

		### define url api call ###

		url3 = 'http://api.songkick.com/api/3.0/venues/%s/calendar.json?apikey=xNZgehDZRT3Xfjpi&jsoncallback=?' % str(self.venueid)

		### use requests to get the api output ###

		r = requests.get(url3)

		### convert the api output to json format ###
		r = json.loads(unidecode(unicodedata.normalize('NFKD', r.text)).encode('utf-8', 'ignore')[2:-2])
		# r = unidecode(unicodedata.normalize('NFKD', r)).encode('ascii', 'ignore')
		# r = json.loads(r.text.encode('utf-8')[2:-2])

		### from this json object, access the artist name, and append to our final list ###

		r = r[u'resultsPage'][u'results'][u'event']

		self.venuename = r[0][u'venue'][u'displayName']
		self.latitude = r[0][u'venue'][u'lat']
		self.longitude = r[0][u'venue'][u'lng']

		for i in range(0, len(r)):
			try:
				self.listofartists.append(r[i][u'performance'][0][u'artist'][u'displayName'])
			except IndexError:
				pass

	### function calls for use in other python scripts ###

	def returnvenuename(self):
		return self.venuename

	def returnvenueid(self):
		return self.venueid

	def returnlist(self):
		return self.listofartists

	def returnlat(self):
		return str(self.latitude)

	def returnlong(self):
		return str(self.longitude)
