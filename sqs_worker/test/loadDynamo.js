var 
    region = process.env.AWS_REGION || "us-west-2",
    AWS = require('aws-sdk');

AWS.config.update({ region: region });

var
    DOC = require("dynamodb-doc"),
    fs = require("fs"),
    uuid=require('uuid'),
    dyn_tablename = process.env.DYN_TABLENAME || "table-imageproc",
    ddb = new DOC.DynamoDB();

function writeDatabase(output) {
    if (output['key'] == undefined) {
        output['key'] = uuid.v4();
    }
    ddb.putItem(
        { "TableName": dyn_tablename, "Item": output},
        function(err,data) {
            if (err) {
                console.log(err, err.stack); // an error occurred
            }
            console.log("Wrote record "+data);
        }
    );
}

if (process.argv[2] == "--files") {
    process.argv.forEach(function (val, index, array) {
      console.log(index + ': ' + val);
      if (index > 2) {
        writeDatabase(JSON.parse(fs.readFileSync(val, "utf8")));
      }
    });
} else
if (process.argv[2] == "--data") {
    var jarray = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
    jarray.forEach(function(val, index, array) {
        writeDatabase(val);
    });
} else {
    console.log("use '--files' or '--data'");
}