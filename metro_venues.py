### python script to get list of venues for a particular metro area ###

### use in venuelocations.py ###

import json
import urllib2
import requests
listofvenueids = set()

metroid = 26330
metroname = "Oakland" # actually city name

# boston area id = 18842
# sf area id = 26330

### define url api call ###

# url = "http://api.songkick.com/api/3.0/metro_areas/%s/calendar.json?apikey=xNZgehDZRT3Xfjpi&jsoncallback=?&page=%s&per_page=50" % (metroid, 1)
# r = requests.get(url)
# r = json.loads(r.text.encode('utf-8')[2:-2])
# r = r[u'resultsPage'][u'results'][u'event']
# print r[0][u'location'][u'city']

citydict = {}
cityset = []

k = 0
for i in range(1, 50):
	url = "http://api.songkick.com/api/3.0/metro_areas/%s/calendar.json?apikey=xNZgehDZRT3Xfjpi&jsoncallback=?&page=%s&per_page=50" % (metroid, i)
	try:
		r = requests.get(url)
		r = json.loads(r.text.encode('utf-8')[2:-2])
		r = r[u'resultsPage'][u'results'][u'event']
		for j in range(0, len(r) + 1):
			k += 1
			cityset.append(r[j][u'location'][u'city'])
			if (r[j][u'location'][u'city'] == '%s, CA, US' % metroname): 
				listofvenueids.add(r[j][u'venue'][u'id'])
				print r[j][u'venue'][u'displayName']
	except Exception:
		pass

listofvenueids.remove(None)
# print listofvenueids

maximum = 0
top = ''
highest = []

for k in cityset:
	if str(k) in citydict:
		citydict[str(k)] += 1
	else:
		citydict[str(k)] = 1

for k, v in citydict.iteritems():
	if v > maximum:
		maximum = v
		top = k

for k, v in citydict.iteritems():
	if v > maximum / 10:
		highest.append((str(k)[:-8]).lower().replace(' ', '_'))

highest.remove(metroname.lower())

f = open("listofvenues_%s.txt" % metroname.lower(), "w")
f.write(str(listofvenueids)[5:-2])
f.close()	

f = open("nearbycities_%s.txt" % metroname.lower(), "w")
f.write(str(highest))
f.close()	