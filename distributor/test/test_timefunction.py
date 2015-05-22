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
import datetime

sys.path.insert(0,'..')
from storyspecification import StorySpecification

time_function = [
	{
		"pct": 10,
		"date_spec":
		{
			"year": "eq(2013)",
			"month": "in(1,4)"
		}
	},
	{
		"pct": 15,
		"date_spec":
		{
			"year": "eq(2013)",
			"month": "in(5,8)"
		}
	},
	{
		"pct": 20,
		"date_spec":
		{
			"year": "eq(2013)",
			"month": "in(9,12)"
		}
	},
	{
		"pct": 25,
		"date_spec":
		{
			"year": "eq(2014)"
		}
	},
	{
		"pct": 30,
		"date_spec":
		{
			"year": "eq(2015)"
		}
	}
]

# time_array = StorySpecification.build_table(time_function)

start = datetime.datetime(2013, 1, 1, 0, 0, 0)
end = datetime.datetime(2015, 12, 31, 11, 59, 59)
count = 2000
td = end - start
delta_second = td.total_seconds() / count
time_now = start
td_incr = datetime.timedelta(seconds=delta_second)
for i in range(0, count):
    if StorySpecification.find_date_match(time_now, time_function):
        print time_now.strftime("%Y-%m-%d %H:%M:%S")
    # else:
    # 	print "not "+time_now.strftime("%Y-%m-%d %H:%M:%S")
    time_now = time_now + td_incr
