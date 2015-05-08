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
