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

import logging, json, boto, flask, os, hashlib
from flask import request, Response
from storyspecification import StorySpecification

import qrcode_generator as QR
import random
import uuid
import psycopg2
import subprocess
import time

import boto
from boto import sts
import boto.dynamodb
import boto.s3

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
bucket_name = os.environ["S3_BUCKET_NAME"]

storySpec = StorySpecification()

def makeImageName(record):
    # Output a string based on stuff
    hash = hashlib.sha1("mymessage".encode("UTF-8")).hexdigest()
    return "QRImage-"+str(random.uniform(0,10))+".jpg"

def makeBucketKey(record):
    # Output a string based on stuff
    key = record["date_time"]
    # put a random string at the beginning
    # remove ':' and ' '
    key = key.replace(':', '')
    key = key.replace(' ', '')
    hash = uuid.uuid4().hex[:4]
    key = hash + '-' + key
    return key

def writeAnImage(record):
    global bucket_name
    print "Writing image for "+json.dumps(record)
    image_file_name = makeImageName(record)
    QR.create_local_image_file(image_file_name, record["product_url"], record["latitude"],
        record["longitude"], record["date_time"], tmpimagefolder+"/")
    key = makeBucketKey(record)
    s3_location = "q/" + key
    # print "aws s3 cp "+tmpimagefolder+"/"+image_file_name+" s3://"+bucket_name+"/"+key+"/"+image_file_name
    QR.upload_file_to_s3(bucket_name, s3_location, image_file_name, tmpimagefolder+"/")

def copytoredshift(record):
    dynamo_table_name = os.environ["DYN_TABLENAME"]
    redshift_username = os.environ["RSDB_USERNAME"]
    redshift_password = os.environ["RSDB_PASSWORD"]
    redshift_database = os.environ["RSDB_DATABASE"]
    redshift_port = os.environ["RSDB_PORT"]
    customer = os.environ["CUSTOMER"]
    cage = os.environ["CAGE"]
    
    role_name = "NucleatorBucketandqDistributorServiceRunner"

    iam_conn = boto.connect_iam()
    role = iam_conn.get_role(role_name)
    role_arn = role["get_role_response"]["get_role_result"]["role"]["arn"]

    stsconn = sts.STSConnection()
    response = stsconn.assume_role(role_arn, "redshift_copy_session")
    access_key = response.credentials.access_key
    secret_key = response.credentials.secret_key
    session_token = response.credentials.session_token

    if customer is "47Lining":
        endpoint = "redshift.%s.%s.com" % (cage, customer)
    else:
        endpoint = "redshift.%s.%s.47lining.com" % (cage, customer)

    print "Connecting to redshift cluster: %s" % endpoint
    conn = psycopg2.connect(dbname=redshift_database, host=endpoint, port=redshift_port, user=redshift_username, password=redshift_password)
    cur = conn.cursor()

    print "Connected. Creating table"
    cur.execute("CREATE TABLE IF NOT EXISTS imageproccessingtable(key varchar(50) NOT NULL, url varchar(200) NOT NULL, dateoriginal timestamp NOT NULL, gpslatitude float8 NOT NULL, gpslongitude float8 NOT NULL, image varchar(100));")
    conn.commit() 
    
    print "Table recreated. Running copy command..."
    cur.execute("copy imageproccessingtable from 'dynamodb://%s' credentials 'aws_access_key_id=%s;aws_secret_access_key=%s;token=%s' readratio 100;" % (dynamo_table_name, access_key, secret_key, session_token))
    conn.commit()  

    print "Copy command completed"

def copyseconddata(record):
    region = os.environ["REGION"]
    dest_bucket_name = os.environ["S3_BUCKET_NAME"]
    source_bucket_name = os.environ["S3_SOURCE_SECOND_BUCKET_NAME"]
    dynamo_table_name = os.environ["DYN_TABLENAME"]

    print "Deleting and recreating dynamo table so only new records are inserted into redshift"
    dynamo_conn = boto.dynamodb.connect_to_region(region)
    table = dynamo_conn.get_table(dynamo_table_name)
    dynamo_conn.delete_table(table)
    dynamo_schema = dynamo_conn.create_schema(hash_key_name='key',hash_key_proto_value=str)
    time.sleep(5)
    print "Sleeping for 5 seconds to let table delete"
    table = dynamo_conn.create_table(name=dynamo_table_name,schema=dynamo_schema,read_units=500, write_units=150)

    role_name = "NucleatorBucketandqDistributorServiceRunner"
    iam_conn = boto.connect_iam()
    role = iam_conn.get_role(role_name)
    role_arn = role["get_role_response"]["get_role_result"]["role"]["arn"]
    stsconn = sts.STSConnection()
    response = stsconn.assume_role(role_arn, "redshift_copy_session")
    access_key = response.credentials.access_key
    secret_key = response.credentials.secret_key
    session_token = response.credentials.session_token

    print "Running S3 Copy Command"
    command = "export AWS_ACCESS_KEY_ID=%s; export AWS_SECRET_ACCESS_KEY=%s; export AWS_SESSION_TOKEN=%s; aws s3 cp s3://%s/ s3://%s/ --recursive --include '*' > /dev/null" % (access_key, secret_key, session_token, source_bucket_name, dest_bucket_name)
    subprocess.call(command, shell=True)

    copytoredshift(record)

def copyinitialdata(record):
    region = os.environ["REGION"]
    dest_bucket_name = os.environ["S3_BUCKET_NAME"]
    source_bucket_name = os.environ["S3_SOURCE_FIRST_BUCKET_NAME"]
    dynamo_table_name = os.environ["DYN_TABLENAME"]

    role_name = "NucleatorBucketandqDistributorServiceRunner"
    iam_conn = boto.connect_iam()
    role = iam_conn.get_role(role_name)
    role_arn = role["get_role_response"]["get_role_result"]["role"]["arn"]
    stsconn = sts.STSConnection()
    response = stsconn.assume_role(role_arn, "redshift_copy_session")
    access_key = response.credentials.access_key
    secret_key = response.credentials.secret_key
    session_token = response.credentials.session_token

    print "Running S3 Copy Command"
    command = "export AWS_ACCESS_KEY_ID=%s; export AWS_SECRET_ACCESS_KEY=%s; export AWS_SESSION_TOKEN=%s; aws s3 cp s3://%s/ s3://%s/ --recursive --include '*' > /dev/null" % (access_key, secret_key, session_token, source_bucket_name, dest_bucket_name)
    subprocess.call(command, shell=True)

    copytoredshift(record)

def handleMessage(message):
    print "Message = ", message
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
    elif "redshift_initial_copy" in message:
        # write the image
        copyinitialdata(message)
    elif "redshift_second_copy" in message:
        # write the image
        copyseconddata(message)

@application.route('/', methods=['POST'])
def proc_message():
    response = None
    if request.json is None:
        # Expect application/json request
        response = Response("", status=415)
    else:
        try:
            # If the message has an SNS envelope, extract the inner message
            if request.json.has_key('TopicArn') and request.json.has_key('Message'):
                message = json.loads(request.json['Message'])
            else:
                message = request.json
            handleMessage(message)
            response = Response("", status=200)
        except Exception as ex:
            logging.exception('Error processing message: %s' % request.json)
            response = Response(ex.message, status=500)
    return response

# here we are going to use boto to up the message visibility timeout
#region = os.environ["REGION"]
#connection = boto.sqs.connect_to_region(region)
#queue = get_queue(queue_name)
#connection.set_queue_attribute(queue, 'VisibilityTimeout', 900) # 15 min

if __name__ == '__main__':
    application.run(host='0.0.0.0')
