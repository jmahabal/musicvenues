import pycountry

print len(pycountry.countries)

final_list = '['

for i in pycountry.countries:
	final_list += '{"alpha2": "' + i.alpha2 + '","name" : "' + str(i.name.encode('ascii', 'ignore')) + '"},'

final_list = final_list[:-1] + "]"

print final_list