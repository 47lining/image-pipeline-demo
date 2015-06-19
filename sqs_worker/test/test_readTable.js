var
	AWS = require('aws-sdk'),
	util = require('util'),
	rt = require("../readTable");
  _      = require('lodash');

var 
    region = process.env.AWS_REGION || "us-west-2",
    dyn_tablename = process.env.DYN_TABLENAME || "table-imageproc";

AWS.config.update({ region: region });

var printResults = function (err, resp) {
  console.log('----------------------------------------------------------------------');
  if(err) {
    console.log('Error running scan', err);
  } else {
    console.log('Found', resp.Count, 'items');
    console.log(util.inspect(_.pluck(resp.Items, 'attrs')));

    if(resp.ConsumedCapacity) {
      console.log('----------------------------------------------------------------------');
      console.log('Scan consumed: ', resp.ConsumedCapacity);
    }
  }

  console.log('----------------------------------------------------------------------');
};

rt.scanMetadata(dyn_tablename, printResults);
