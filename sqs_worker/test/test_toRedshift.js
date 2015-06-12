var
	AWS = require('aws-sdk'),
	util = require('util'),
	rsCopy = require("../toRedshift");

var
 util   = require('util'),
 _      = require('lodash');

var printResults = function (err, resp) {
  console.log('----------------------------------------------------------------------');
  if(err) {
    console.log('Error running scan', err);
  }

  console.log('----------------------------------------------------------------------');
};

rsCopy.copyToRedshift("us-west-2", "table-imageproc", "", printResults);