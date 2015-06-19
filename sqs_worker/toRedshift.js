var
	pg = require('pg'),
	AWS = require('aws-sdk'),
	uuid = require('uuid'),
	src_path = process.env.MODULE_PATH || ".",
	readTable = require(src_path+"/readTable"),
    rs_username = process.env.RSDB_USERNAME || "imagedb",
    rs_password = process.env.RSDB_PASSWORD || "ImageDbuser7",
    rs_database = process.env.RSDB_DATABASE || "defaultdb",
    debug = "true" == (process.env.APP_DEBUG || "false"),
    rs_port = process.env.RSDB_PORT || 5439,
    cage = process.env.CAGE || "ci",
    customer = process.env.CUSTOMER || "shoppertrak",
    rs_host = process.env.RSDB_HOST || "redshift."+cage+"."+customer+".47lining.com",
	rsCopy = new Object();

function writeDynamoToRedshift(table, callback) {
    writeToRedshift("'dynamodb://"+table+"'", "READRATIO 100", callback);
}

function writeS3ToRedshift(bucketName, key, callback) {
    writeToRedshift("'s3://"+bucketName+"/"+key+"'", " JSON 'auto'", callback);
}

function writeToRedshift(from_str, args, callback) {
    var client = new pg.Client(
    {
        user: rs_username,
        database: rs_database,
        password: rs_password,
        port: rs_port,
        host: rs_host
    });
    var query = "COPY imageprocessingtable from "+ from_str
            +" credentials 'aws_access_key_id="+AWS.config.credentials.accessKeyId+";aws_secret_access_key="+AWS.config.credentials.secretAccessKey+"' "
            + args
            +" TIMEFORMAT AS 'YYYY:MM:DD HH:MI:SS' "
    ;
    if (debug) console.log("RS Query: "+query);
    var outer_callback = callback;
    client.connect(function(err) {
        if (err) {
            console.log("ERROR: "+err);
            outer_callback(err);
            return;
        }
        client.query(query, "",
            function(err, result) {
                if (debug) console.log(">>> query callback.. ");
                client.end();
                if (err) {
                    console.log("ERROR: "+err);
                }
                if (outer_callback) {
                    if (debug) console.log(">>> outer callback.. ");
                    outer_callback(err, result);
                    if (debug) console.log("<<< outer callback.. ");
                }
                if (debug) console.log("<<< query callback.. ");
            }
        );
        if (debug) console.log("<<< connect callback.. ");
    });
    if (debug) console.log("<<< writeToRedshift");
}

function writeToS3(dynamo_data, callback) {
    // N.B. this might take a wad of memory all items and strings - 
    // TODO look at stream implementation
    bucketName = 'dynamo-archive-'+uuid.v4();
    console.log(">>> writingTo S3 bucket "+bucketName+", rows: "+dynamo_data.length);
	var output_data = "";
	for (i = 0; i < dynamo_data.length; i++) {
		output_data = output_data + JSON.stringify(dynamo_data[i].attrs);
	}
    var s3 = new AWS.S3();
    s3.createBucket({Bucket: bucketName}, function(err, data) {
        if (err) console.log(err, err.stack); // an error occurred
        else {
            // console.log(">>> s3.upload.. ");
            s3.putObject({Bucket: bucketName, Body: output_data, Key: 'imageproc.json'}, function(err, data) {
                if (err) console.log(err, err.stack); // an error occurred
                else {
                    writeToRedshift(bucketName, 'imageproc.json', callback);
                }
			});
        }
    });
}

rsCopy.copyDynamoToRedshiftViaS3 = function(region, dyn_tablename, query_data, callback) {
    if (debug) console.log(">>> copyToRedshiftViaS3: "+dyn_tablename);
	AWS.config.update({ region: region });
	readTable.scanMetadata(dyn_tablename, 
		function(err, data) {
			if (err) {
				console.log(err);
				callback(err);
				return;
			}
			writeToS3(data.Items, callback);
		}
	);
};

rsCopy.copyDynamoToRedshift = function(region, dyn_tablename, query_data, callback) {
    if (debug) console.log(">>> copyToRedshift: "+dyn_tablename);
    AWS.config.update({ region: region });
    writeDynamoToRedshift(dyn_tablename, callback);
};
module.exports=rsCopy;
