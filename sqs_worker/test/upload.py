import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.sts import STSConnection

conn = S3Connection()
s3_bucket = conn.get_bucket("bucket-testingfulltest-test6-shoppertrak", validate=False)
s3_key = Key(s3_bucket)
s3_key.key = "im.jpg"
s3_key.set_contents_from_filename("im.jpg")
s3_key.set_acl('authenticated-read')
