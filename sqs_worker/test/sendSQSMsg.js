var 
    region = process.env.AWS_REGION || "us-west-2",
    sqsq = process.env.SQS_QUEUE || "https://sqs.us-west-2.amazonaws.com/172139249013/sqs-queue-impagep3-test1-47lining",
    AWS = require('aws-sdk');

AWS.config.update({ region: region });
var
	sqs = new AWS.SQS();

var params = {
  MessageBody: '{"operation": "copyToRedshift"}',
  QueueUrl: sqsq,
  DelaySeconds: 0,
};
//   MessageBody: '{"operation": "copyToS3Redshift"}',

sqs.sendMessage(params, function(err, data) {
  if (err) console.log(err, err.stack); // an error occurred
  else     console.log(data);           // successful response
});