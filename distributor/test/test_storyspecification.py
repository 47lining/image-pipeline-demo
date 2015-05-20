# Copyright 2015 47Lining LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
