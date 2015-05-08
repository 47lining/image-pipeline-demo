# Copyright 2013. Amazon Web Services, Inc. All Rights Reserved.
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

import logging, json, boto, flask, os
from flask import request, Response
from storyspecification import StorySpecification

import qrcode_generator as QR

# Create and configure the Flask app
application = flask.Flask(__name__)
application.debug = True
# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler
LOG_FILE = '/tmp/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

tmpimagefolder = "tmpimagefolder"

if not os.path.isdir(tmpimagefolder):
    os.mkdir(tmpimagefolder)

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)
image_number = 0
bucket_name = os.environ["S3_BUCKET_NAME"]

storySpec = StorySpecification()

def makeImageName(record):
    # Output a string based on stuff
    global image_number
    image_number = image_number + 1
    return "QRImage"+str(image_number)+".jpg"

def makeBucketKey(record):
    # Output a string based on stuff
    return record["date_time"]

def writeAnImage(record):
    global bucket_name
    print "Writing image for "+json.dumps(record)
    image_file_name = makeImageName(record)
    QR.create_local_image_file(image_file_name, record["product_url"], record["latitude"],
        record["longitude"], record["date_time"], tmpimagefolder+"/")
    QR.upload_file_to_s3(bucket_name, makeBucketKey(record), image_file_name, tmpimagefolder+"/")

@application.route('/', methods=['POST'])
def proc_message():
    response = None
    if request.json is None:
        # Expect application/json request
        response = Response("", status=415)
    else:
        message = dict()
        try:
            # If the message has an SNS envelope, extract the inner message
            if request.json.has_key('TopicArn') and request.json.has_key('Message'):
                message = json.loads(request.json['Message'])
            else:
                message = request.json
            if "date" in message:
                msg_date = message["date"]
                if storySpec.generate_record(msg_date):
                    record = storySpec.create_record(msg_date)
                    # write the image
                    writeAnImage(record)
                else:
                    print "Choosing not to write image for "+msg_date
            elif "product_url" in message:
                # write the image
                writeAnImage(message)
            response = Response("", status=200)
        except Exception as ex:
            logging.exception('Error processing message: %s' % request.json)
            response = Response(ex.message, status=500)

    return response

if __name__ == '__main__':
    application.run(host='0.0.0.0')