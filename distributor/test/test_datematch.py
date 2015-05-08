import sys
import datetime

sys.path.insert(0,'..')
from storyspecification import StorySpecification

daten = datetime.datetime(2015, 4, 15, 12, 30, 0)
if not StorySpecification.date_match(daten, {"year": "eq(2015)"}):
	print "FAIL: No match on year eq(2015)"
if not StorySpecification.date_match(daten, {"month": "eq(4)"}):
	print "FAIL: No match on month eq(4)"
if not StorySpecification.date_match(daten, {"day": "eq(15)"}):
	print "FAIL: No match on day eq(15)"
if not StorySpecification.date_match(daten, {"hour": "eq(12)"}):
	print "FAIL: No match on hour eq(12)"
if not StorySpecification.date_match(daten, {"min": "eq(30)"}):
	print "FAIL: No match on min eq(30)"


if not StorySpecification.date_match(daten, 
	{"min": "eq(30)", "hour":"eq(12)"}):
	print "FAIL: Not match on min eq(30) and hour eq(12)"
if StorySpecification.date_match(daten,
	{"year": "eq(2015)", "hour":"eq(4)"}):
	print "FAIL: Match on year eq(2015) and hour eq(4)"
if not StorySpecification.date_match(daten,
	{"year": "eq(2015)", "month":"in(2,4)"}):
	print "No match on year eq(2015) and month in(2,4)"
