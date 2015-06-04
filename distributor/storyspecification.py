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
import json, re, logging
from random import uniform, randint
from datetime import datetime, timedelta

class StorySpecification(object):

    def __init__(self, spec_file="specification.json"):
        with open(spec_file, "r") as myfile:
            data = myfile.read()
        self.specification = json.loads(data)
        self.product_codes = self.specification['specification'][0]['product_codes']
        self.product_code_table = StorySpecification.build_table(self.product_codes)
        self.geocodes = self.specification['specification'][0]['geolocations']
        self.geocode_table = StorySpecification.build_table(self.geocodes)
        self.time_function = self.specification['specification'][0]['time_function']
        self.hour_distribution = self.specification['specification'][0]['hour_distribution']
        self.hour_table = StorySpecification.build_table(self.hour_distribution)

    # Given an input dict with 'pct' entries, build an output table
    # with cumulative percentages
    @staticmethod
    def build_table(input_array):
        cumulative_pct = 0
        output_array = []
        for item in input_array:
            cumulative_pct = cumulative_pct + item['pct']
            output_array.append(cumulative_pct)
        return output_array

    @staticmethod
    def find_entry(entries, percentages_array):
        if len(percentages_array) != len(entries):
            raise ValueError("percentages should match entries")
        val = randint(1, 100)
        for i in range(0, len(percentages_array)):
            if val <= percentages_array[i]:
                # print "Random no. is "+str(val)+", i is "+str(i)
                return entries[i]
        # print "Random no. is "+str(val)+", i is MAX"
        return entries[len(entries)-1]

    @staticmethod
    def spec_match(value, spec):
        logging.info("Trying to match '%s'" % spec)
        spec_ex = re.compile("(\w\w)\((\d+),?(\d*)\)")
        res = spec_ex.match(spec)
        if not res:
            logging.exception("Spec string not correct format '%s'" % spec)
            raise ValueError("Spec string not correct format")
        op = res.group(1)
        v1 = int(res.group(2))
        v2 = res.group(3)
        if op == "eq":
            return value == v1
        if op == "lt":
            return value < v1
        if op == "le":
            return value <= v1
        if op == "gt":
            return value > v1
        if op == "ge":
            return value >= v1
        if op == "lt":
            return value < v1
        if op == "in":
            if len(v2)==0:
                raise ValueError("The 'in' operator must have two values")
            return value >= v1 and value <= int(v2)
        raise ValueError("Unrecognized operator '"+op+"'")

    @staticmethod
    def date_match(date, specification):
        if type(date) == unicode:
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        elif type(date) != datetime:
            raise ValueError("date_match only handles strings and datetime objs - you passed in "+str(type(date)))
        if "year" in specification:
            if not StorySpecification.spec_match(date.year, specification["year"]):
                return False
        if "month" in specification:
            if not StorySpecification.spec_match(date.month, specification["month"]):
                return False
        if "day" in specification:
            if not StorySpecification.spec_match(date.day, specification["day"]):
                return False
        if "hour" in specification:
            if not StorySpecification.spec_match(date.hour, specification["hour"]):
                return False
        if "min" in specification:
            if not StorySpecification.spec_match(date.minute, specification["min"]):
                return False
        return True

    @staticmethod
    def find_date_match(date, entries):
        for entry in entries:
            if StorySpecification.date_match(date, entry['date_spec']):
                pct = entry['pct']
                val = uniform(0.0, 100.0)
                return val <= pct
        raise ValueError("No date match for "+date.strftime("%Y-%m-%d %H:%M:%S"))

    def generate_record(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return StorySpecification.find_date_match(date, self.time_function)

    def create_record(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        product_url = StorySpecification.find_entry(self.product_codes, self.product_code_table)
        location = StorySpecification.find_entry(self.geocodes, self.geocode_table)
        hour = StorySpecification.find_entry(self.hour_distribution, self.hour_table)
        date = date + timedelta(hours=hour['hour'])
        return {
            "product_url": product_url['url'],
            "date_time": date.strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": location['latitude'],
            "longitude": location['longitude']
        }
