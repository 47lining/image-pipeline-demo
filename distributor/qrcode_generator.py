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
import pyexiv2
import qrcode
import random
import math
import yaml
import datetime
import json
import boto
import time
import sys
import os

from datetime import datetime

from fractions import Fraction

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from boto.sts import STSConnection

def decimal_to_dms(decimal):
    """Convert decimal degrees into degrees, minutes, seconds.

    >>> decimal_to_dms(50.445891)
    [Fraction(50, 1), Fraction(26, 1), Fraction(113019, 2500)]
    >>> decimal_to_dms(-125.976893)
    [Fraction(125, 1), Fraction(58, 1), Fraction(92037, 2500)]
    """
    remainder, degrees = math.modf(abs(decimal))
    remainder, minutes = math.modf(remainder * 60)

    degrees = Fraction(degrees).limit_denominator(9999999)
    minutes = Fraction(minutes).limit_denominator(9999999)
    seconds = Fraction(remainder * 60).limit_denominator(9999999)

    #print dms_to_decimal(degrees, minutes, seconds)

    return [degrees, minutes, seconds]

def create_local_image_file(image_name, url, gps_lat, gps_long, datetime, temp_file_location):

	img = qrcode.make(url)
	img.save("%s%s" % (temp_file_location, image_name), "jpeg")

	metadata = pyexiv2.ImageMetadata("%s%s" % (temp_file_location, image_name))
	metadata.read()

	latitude = decimal_to_dms(gps_lat)
	longitude = decimal_to_dms(gps_long)

	key = 'Exif.Image.DateTimeOriginal'
	value = datetime
	metadata[key] = value

	key = 'Exif.GPSInfo.GPSLatitude'
	value = latitude
	metadata[key] = value

	if gps_lat < 0:
		value = 'S'
	else:
		value = 'N'
	key = 'Exif.GPSInfo.GPSLatitudeRef'
	metadata[key] = value

	key = 'Exif.GPSInfo.GPSLongitude'
	value = longitude
	metadata[key] = value

	if gps_lat < 0:
		value = 'E'
	else:
		value = 'W'
	key = 'Exif.GPSInfo.GPSLongitudeRef'
	metadata[key] = value

	metadata.write()

def upload_file_to_s3(bucket_name, s3_location, image_name, temp_file_location):

	conn = S3Connection()
	s3_bucket = conn.get_bucket(bucket_name, validate=False)
	s3_key = Key(s3_bucket)
	s3_key.key = "%s/%s" % (s3_location, image_name)
	s3_key.set_contents_from_filename("%s%s" % (temp_file_location, image_name))
	s3_key.set_acl('authenticated-read')

def create_qr_image_file(bucket_name=None, s3_location=None, image_name=None, url=None, gps_lat=None, gps_long=None, datetime=None):

	#Need to set new temp file location
	temp_file_location = "/tmp/"

	create_local_image_file(image_name, url, gps_lat, gps_long, datetime, temp_file_location)
	if not bucket_name is None:
		upload_file_to_s3(bucket_name, s3_location, image_name, temp_file_location)
