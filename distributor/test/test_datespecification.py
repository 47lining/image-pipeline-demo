import sys

sys.path.insert(0,'..')
from storyspecification import StorySpecification

# ********* EQ ********
if not StorySpecification.spec_match(5, "eq(5)"):
	print "FAIL: 5 not eq(5)"
if StorySpecification.spec_match(5, "eq(6)"):
	print "FAIL: 5 is eq(6)"
# ********* LT ********
if not StorySpecification.spec_match(5, "lt(6)"):
	print "FAIL: 5 not lt(6)"
if StorySpecification.spec_match(5, "lt(4)"):
	print "FAIL: 5 is lt(4)"
if StorySpecification.spec_match(5, "lt(5)"):
	print "FAIL: 5 is lt(5)"
# ********** LE ********
if not StorySpecification.spec_match(5, "le(6)"):
	print "FAIL: 5 not le(6)"
if StorySpecification.spec_match(5, "le(4)"):
	print "FAIL: 5 is le(4)"
if not StorySpecification.spec_match(5, "le(5)"):
	print "FAIL: 5 not le(5)"
# ********* GT ********
if not StorySpecification.spec_match(5, "gt(4)"):
	print "FAIL: 5 not gt(4)"
if StorySpecification.spec_match(5, "gt(6)"):
	print "FAIL: 5 is gt(6)"
if StorySpecification.spec_match(5, "gt(5)"):
	print "FAIL: 5 is gt(5)"
# ********** GE ********
if not StorySpecification.spec_match(5, "ge(4)"):
	print "FAIL: 5 not ge(4)"
if StorySpecification.spec_match(5, "ge(6)"):
	print "FAIL: 5 is ge(6)"
if not StorySpecification.spec_match(5, "ge(5)"):
	print "FAIL: 5 not ge(5)"
# ********** IN ********
if not StorySpecification.spec_match(5, "in(4,6)"):
	print "FAIL: 5 not in(4,6)"
if not StorySpecification.spec_match(5, "in(5,10)"):
	print "FAIL: 5 not in(5,10)"
if not StorySpecification.spec_match(5, "in(1,5)"):
	print "FAIL: 5 not in(1,5)"
if StorySpecification.spec_match(5, "in(6,10)"):
	print "FAIL: 5 is in(6,10)"
if StorySpecification.spec_match(5, "in(1,4)"):
	print "FAIL: 5 is in(1,4)"
