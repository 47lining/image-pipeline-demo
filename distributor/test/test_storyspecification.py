import sys

sys.path.insert(0,'..')
from storyspecification import StorySpecification

input_array = [
		{
			"url": "https://www.apple.com/iphone-6/",
			"pct": 30
		},
		{
			"url": "https://www.apple.com/watch/",
			"pct": 10
		},
		{
			"url": "https://www.apple.com/ipad-air-2/",
			"pct": 50
		},
		{
			"url": "https://www.apple.com/macbook-pro/",
			"pct": 10
		}
]

product_codes = StorySpecification.build_table(input_array)
# for i in range(len(product_codes)):
	# print "PC "+str(i)+": "+str(product_codes[i])+": "+str(input_array[i])

for i in range(1000):
	# import pdb; pdb.set_trace()
	pc = StorySpecification.find_entry(input_array, product_codes)
	print pc['url']
