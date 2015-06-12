var
	AWS = require('aws-sdk'),
	util = require('util'),
	rt = require("../readTable");

var
 util   = require('util'),
 _      = require('lodash');

AWS.config.update({ region: "us-west-2" });

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

rt.scanMetadata("table-imageproc", printResults);
