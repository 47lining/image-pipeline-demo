var
	AWS = require('aws-sdk'),
	util = require('util'),
	rsCopy = require("../toRedshift");
	_      = require('lodash');

var 
    region = process.env.AWS_REGION || "us-west-2",
    dyn_tablename = process.env.DYN_TABLENAME || "table-imageproc",

var printResults = function (err, resp) {
  console.log('----------------------------------------------------------------------');
  if(err) {
    console.log('Error running scan', err);
  }

  console.log('----------------------------------------------------------------------');
};

rsCopy.copyDynamoToRedshiftViaS3(region, dyn_tablename, "", printResults);

rsCopy.copyDynamoToRedshift(region, dyn_tablename, "", printResults);