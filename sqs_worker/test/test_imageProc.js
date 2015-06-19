var
	AWS = require('aws-sdk'),
	util = require('util'),
    imageProc = require("../imageProc");

var printResults = function (err, resp) {
  console.log('----------------------------------------------------------------------');
  if(err) {
    console.log('Error running scan', err);
  }
  console.log('----------------------------------------------------------------------');
};
var 
    bucket = process.env.BUCKET || "bucket-imageproc",
    key = process.env.FILE || "QRImage1.jpg";

imageProc.readFile(bucket, key, printResults);
