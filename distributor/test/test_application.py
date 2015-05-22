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
import application as APP
from storyspecification import StorySpecification

storyspecification = StorySpecification(spec_file="../specification.json")
record = storyspecification.create_record("2015-01-01 13:59:59")

print "Product url: "+record["product_url"]
print "Date time: "+record["date_time"]
print "latitude: "+str(record["latitude"])
print "longitude: "+str(record["longitude"])

APP.writeAnImage(record)
