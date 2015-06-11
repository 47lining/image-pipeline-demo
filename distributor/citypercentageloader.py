import json
import random

stream = open("/Users/EricPutney/.nucleator/contrib/bucketandq/distributor/specification.json")
specification = json.load(stream)

for type in specification["specification"]:

	numberofcities = len(type["geolocations"])

	totalpercent = 0
	for city in type["geolocations"]:
		#print city

		longcounter = (city["longitude"] + 160)/24 + 1
		longcounter = 7.5 - longcounter
		print longcounter

		randomCounter = random.uniform(1, 10)
		#print randomCounter

		percentage = (randomCounter * longcounter) / (20 * numberofcities)
		totalpercent = totalpercent + percentage

		city["pct"] = percentage * 100
		#print city

stream = open("/Users/EricPutney/.nucleator/contrib/bucketandq/distributor/specification.json", "w+")
stream.write(json.dumps(specification, sort_keys=True, indent=4, separators=(',', ': ')))

print totalpercent