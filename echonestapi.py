# echonest api calls

### import pyechonest ###

from pyechonest import config
config.ECHO_NEST_API_KEY="TN16YTOGOH7H4MUJ2"
from pyechonest import artist
from pyechonest import util
import venuelocations
import json
import unicodedata
import requests_cache
import requests
import codecs
import pycountry
import numpy
from unidecode import unidecode
import time

requests_cache.install_cache('demo_cache1')


### initialize the final dictionary (to be used for pie chart) ###

### edit the following || echonestapi: city // metro_venues: metroid, metroname // apitest: data, citymap, projection  ###

city = "oakland" # lowercase

city_genre_weights = {}
venueidlist = open("listofvenues_%s.txt" % city).read()
venueidlist = (venueidlist.replace(",",' ').split())
counter = 1
ratec = 0

nearbycities = open("nearbycities_%s.txt" % city).read()


totalartists = 0
artists_SF = 0
artists_CA = 0
artists_US = 0
artist_countries = []

colordict = { 'rock': '#2c3e50',
			  'pop': '#1abc9c',
			  'indie': '#3498db',
			  'jazz': '#f1c40f',
			  'electronic': '#e74c3c'
	}


f = open("json/venueoutput_%s.json" % city, "w")
f.write('[')

for q in venueidlist:
	venue_genre_weights = {}
	a = venuelocations.Venue(q)

	# print a.returnvenueid

	### build the list of artists from a venue ###
	if (a.returnlat() != "None"):

		artist_list = a.returnlist()
		# print a.returnvenuename()
		# print artist_list

		### create list of all genres from all artists and their weights ###
		venue_artist_countries_a = []
		artistterms = []
		for i in range(0, len(artist_list)):
			print artist_list[i]
			#vb = (artist.Artist(artist_list[i]).terms)
			temp_genre = requests.get("http://developer.echonest.com/api/v4/artist/terms?api_key=TN16YTOGOH7H4MUJ2&name=%s&format=json" % artist_list[i])
			temp_location = requests.get("http://developer.echonest.com/api/v4/artist/profile?api_key=TN16YTOGOH7H4MUJ2&name=%s&format=json&bucket=artist_location" % artist_list[i])
			temp_genre = json.loads(temp_genre.text)
			temp_location = json.loads(temp_location.text)
			# print temp_location
			if temp_genre[u'response'][u'status'][u'code'] == 5:
				temp_genre = [{u'name': u'unknown', u'weight': .1}]
				temp_location = u'Unknown'
			else:
				# print temp_genre
				temp_genre = temp_genre[u'response'][u'terms']
				try:
					temp_location = temp_location[u'response'][u'artist'][u'artist_location']
				except KeyError:
					temp_location = u'Unknown'
			if len(temp_genre) == 0:
				temp_genre = [{u'name': u'unknown', u'weight': .1}]
			if temp_location == None:
				temp_location = u'Unknown'

			ratec += 1
			# print "location", temp_location
			# print ratec
			if ratec == 118:
				print "API Rate hit, sleeping"
				# time.sleep(60)
				ratec = 0
			artistterms = artistterms + temp_genre

			totalartists += 1
			if temp_location != u'Unknown':
				if temp_location[u'country'] == u'United States':
					if temp_location[u'region'] == u'CA':
						if temp_location['city'] == u'San Francisco':
							artists_SF += 1
						else:
							artists_CA += 1
					else:
						artists_US += 1
				else:
					try:
						# artist_countries.append(temp_location[u'country'])
						v = pycountry.countries.get(name=temp_location[u'country']).alpha2
						venue_artist_countries_a.append(v)
					except KeyError:
						pass

		venue_artist_countries_b = list(set(venue_artist_countries_a))
		venue_artist_countries = ''
		for i in venue_artist_countries_b:
			venue_artist_countries += "countries_" + str(i).lower() + " "
		# print venue_artist_countries

		if len(venue_artist_countries_a) > 0:
			artist_countries += venue_artist_countries_a

			# except util.EchoNestAPIError:
			# 	pass

		### to our main list, add the weights, creating keys as necessary ###

		for i in range(0, len(artistterms)):
			if artistterms[i][u'name'] in venue_genre_weights:
				venue_genre_weights[artistterms[i][u'name']] += artistterms[i][u'weight']
			else:
				venue_genre_weights[artistterms[i][u'name']] = artistterms[i][u'weight']
			if artistterms[i][u'name'] in city_genre_weights:
				city_genre_weights[artistterms[i][u'name']] += artistterms[i][u'weight']
			else:
				city_genre_weights[artistterms[i][u'name']] = artistterms[i][u'weight']

		### steps to remove non-major genres ###

		# print venue_genre_weights

		def quantiled(weights, s):
			temp_glist = []
			for k, v in weights.iteritems():
				temp_glist.append(v)
			temp_len_glist = len(temp_glist)
			# print temp_len_glist, s
			if temp_len_glist <= s:
				return 0
			else:
				# print (temp_len_glist - s) / float(temp_len_glist)
				return numpy.percentile(temp_glist, ((temp_len_glist - s) / float(temp_len_glist) * 100))

		meanw = quantiled(venue_genre_weights, 10)

		# def meanweights(weights):
		# 	meanweights = 0
		# 	for k, v in venue_genre_weights.iteritems():
		# 		meanweights += v
		# 	if len(venue_genre_weights) == 0:
		# 		return 0
		# 	else:
		# 		return meanweights / (len(venue_genre_weights))

		# meanw = (meanweights(venue_genre_weights))
		# print meanw, "meanw"
		# print quantiled(temp_glist), "quantiled"

		current_largest = 0
		current_largest_genre = []

		for k, v in venue_genre_weights.iteritems():
			if v > current_largest and v > 0.1 and k not in current_largest_genre:
				current_largest = v
				current_largest_genre = []
				current_largest_genre.append(str(k.encode('ascii', 'ignore')))
			elif v == current_largest and k not in current_largest_genre:
				current_largest_genre.append(str(k.encode('ascii', 'ignore')))

		for k, v in venue_genre_weights.iteritems():
			if v < meanw:
				# del k
				venue_genre_weights[k] = 0.00001

		#print current_largest_genre, str(current_largest_genre)[2:-2]
		ewr = 'genres' + str(current_largest_genre)[2:-2]
		# print ewr
		# print venue_genre_weights

		### sanitize the dictionary to prepare for pie chart ###

		final_list = []
		for k, v in venue_genre_weights.iteritems():
			if k in colordict:
				final_list.append("{" + '"label": "' + k + '", "' + 'value": ' + str(v) + ', "' + 'color": "' + colordict[k] + '"}')
			else:
				final_list.append("{" + '"label": "' + k + '", "' + 'value": ' + str(v) + "}")
		for i in range(0, len(final_list)):
			try:
				final_list[i] = unidecode(unicodedata.normalize('NFKD', final_list[i])).encode('ascii', 'ignore')
			except UnicodeEncodeError:
				pass
				# final_list[i] = '{}'

		final_list = ','.join(final_list)
		final_list = '{"venuename": "' + a.returnvenuename() + '",' '"data": {"latitude": "' + a.returnlat() + '", "longitude": "' + a.returnlong() + '", "countries": "' + str(venue_artist_countries) + '", "topgenre": "' + ewr + '"}, "labels": [' + final_list + ']},'

		### output our weighted genre dictionary ###
		# print counter
		counter += 1
		f.write(str(final_list))

### create the music profile for the entire city ###

# def city_meanweights(weights):
# 	city_meanweights = 0
# 	for k, v in city_genre_weights.iteritems():
# 		city_meanweights += v
# 	if len(city_genre_weights) != 0:
# 		return city_meanweights / (len(city_genre_weights))
# 	else:
# 		return city_meanweights
# print city_genre_weights

city_meanw = quantiled(city_genre_weights, 15)
# print city_meanw

#city_meanw = (city_meanweights(city_genre_weights) * 6)

for k, v in city_genre_weights.iteritems():
	if v < city_meanw:
		# del k
		city_genre_weights[k] = 0.00001

# print city_genre_weights

# print city_genre_weights

city_final_list = []
for k, v in city_genre_weights.iteritems():
	if k in colordict:
		city_final_list.append("{" + '"label": "' + k + '", "' + 'value": ' + str(v) + ', "' + 'color": "' + colordict[k] + '"}')
	else:
		city_final_list.append("{" + '"label": "' + k + '", "' + 'value": ' + str(v) + "}")
for i in range(0, len(city_final_list)):
	try:
		city_final_list[i] = unidecode(unicodedata.normalize('NFKD', city_final_list[i])).encode('ascii', 'ignore')
	except UnicodeEncodeError:
		pass

city_final_list = ','.join(city_final_list)

artist_countries = list(set(artist_countries))

print nearbycities

city_final_list = '{"cityname": "' + city + '", "nearbycities": "' + str(nearbycities) + '","countries": "' + str(artist_countries) + '", "labels": [' + city_final_list + ']}'

# print "artists_SF:", artists_SF, "artists_CA:", artists_CA + artists_SF, "artists_US:", artists_SF + artists_CA + artists_US
# print artist_countries, len(artist_countries)
# print "total artists:", totalartists
# print artist_countries[0], "isitalist"

### write to file ###

f.write(str(city_final_list))
f.write(']')
f.close()
