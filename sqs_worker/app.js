// Message Format:
// {
//   "Records": [
//     {
//       "eventVersion": "2.0",
//       "eventSource": "aws:s3",
//       "awsRegion": "us-west-2",
//       "eventTime": "2015-03-26T19:50:07.299Z",
//       "eventName": "ObjectCreated:Put",
//       "userIdentity": {
//         "principalId": "AWS:AIDAJQULG4WG7WMOOT4P6"
//       },
//       "requestParameters": {
//         "sourceIPAddress": "10.240.35.42"
//       },
//       "responseElements": {
//         "x-amz-request-id": "C0C0FB75FEA5008C",
//         "x-amz-id-2": "XwRDeuzN5Hlf5ZDx6Tfz2VQQM8ixAHSnAuOy7XVCz9PucamfMcRwLUj3SzpwdXaU"
//       },
//       "s3": {
//         "s3SchemaVersion": "1.0",
//         "configurationId": "TestPut",
//         "bucket": {
//           "name": "bucket-imageproc-test1-47lining",
//           "ownerIdentity": {
//             "principalId": "AR6S9OMB6DGSQ"
//           },
//           "arn": "arn:aws:s3:::bucket-imageproc-test1-47lining"
//         },
//         "object": {
//           "key": "images\/iphone_4s_pic.jpg",
//           "size": 915456,
//           "eTag": "44e0e068ff0cf74ac50ccb1e0638b8d2"
//         }
//       }
//     }
//   ]
// }
var 
    port = process.env.PORT || 3000,
    region = process.env.AWS_REGION || "us-west-2",
    dyn_tablename = process.env.DYN_TABLENAME || "table-imageproc",
    http = require('http'),
    rsCopy = require("./toRedshift"),
    imageProc = require("./imageProc"),
    fs = require('fs'),
    AWS = require('aws-sdk'),
    DOC = require("dynamodb-doc"),
    html = fs.readFileSync('index.html'),
    uuid=require('uuid'),
    gm = require('gm'),
    Canvas = require('canvas'),
    Image = Canvas.Image,
    qrcode = require('jsqrcode')(Canvas),
    s3 = new AWS.S3(),
    ddb = new DOC.DynamoDB();

AWS.config.update({ region: region });

function writeDatabase(output, res) {
    if (output['key'] == undefined) {
        output['key'] = uuid.v4();
    }
    ddb.putItem(
        { "TableName": dyn_tablename, "Item": output},
        function(err,data) {
            if (err) {
                console.log(err, err.stack); // an error occurred
                res.writeHead(500, 'Error writing record', {'Content-Type': 'text/plain'});
            } else {
                // console.log(data);
                res.writeHead(200, 'OK', {'Content-Type': 'text/plain'});
            }
            res.end();
        }
    );
}

function Callback(response) {
    this.res = response;
    this.std_callback = (function(err, data) {
        if (err) {
            console.log(err, err.stack); // an error occurred
            this.res.writeHead(500, 'Error writing record', {'Content-Type': 'text/plain'});
            this.res.end();
        } else {
            // console.log(data);
            if (err == undefined && typeof data == 'string') {
                console.log("Finished no error: "+data);
                this.res.writeHead(200, data, {'Content-Type': 'text/plain'});
                this.res.end();
            } else {
                writeDatabase(data, this.res);
            }
        }
    }).bind(this);
}

function handleMessage(data, res) {
    try {
        var obj = JSON.parse(data);
        if (obj.operation != undefined && obj.operation == 'copyToS3Redshift') {
            console.log('Received dyn2s3red message: ' + data);
            cb = new Callback(res);
            rsCopy.copyDynamoToRedshiftViaS3(region, dyn_tablename, data, cb.std_callback);
            return;
        }
        else if (obj.operation != undefined && obj.operation == 'copyToRedshift') {
            console.log('Received dyn2red message: ' + data);
            cb = new Callback(res);
            rsCopy.copyDynamoToRedshift(region, dyn_tablename, data, cb.std_callback);
            return;
        }

        console.log("Processing msg count: "+obj.Records.length)
        for (var r in obj.Records) {
            // TODO >1 record in the message?
            record = obj.Records[r];
            if (record.eventName == undefined || record.eventName.lastIndexOf("ObjectCreated:",0) != 0) {
                // not a message we're interested in, but have daemon remove message
                res.writeHead(200, 'OK', {'Content-Type': 'text/plain'});
                res.end();
            }
            else if (typeof record.s3.bucket.name === "undefined") {
                console.log("No bucket name in message");
                res.writeHead(500, 'OK', {'Content-Type': 'text/plain'});
                res.end();
            }
            else if (typeof record.s3.object.key === "undefined") {
                console.log("No file element in message");
                res.writeHead(500, 'OK', {'Content-Type': 'text/plain'});
                res.end();
            } else {
                cb = new Callback(res);
                imageProc.readFile(record.s3.bucket.name, record.s3.object.key, cb.std_callback);
            }
        }
    }
    catch (err) {
        if (err) console.log(err, err.stack); // an error occurred
        res.writeHead(500, 'OK', {'Content-Type': 'text/plain'});
        res.end();
    }
}

var server = http.createServer(function (req, res) {
    if (req.method === 'POST') {
        var body = '';

        req.on('data', function(chunk) {
            body += chunk;
        });

        req.on('end', function() {
            if (req.url === '/') {
                console.log('Received message: ' + body);
                handleMessage(body, res);
            } else if (req.url === '/heartbeat') {
                res.writeHead(200, 'OK', {'Content-Type': 'text/plain'});
                res.end();
            } else {
                res.writeHead(404, 'Not Found', {'Content-Type': 'text/plain'});
                res.end();
            }
        });
    } else {
        res.writeHead(200);
        res.write(html);
        res.end();
    }
});

// Listen on port 3000, IP defaults to 127.0.0.1
server.listen(port);

// Put a friendly message on the terminal
console.log('Server running at http://127.0.0.1:' + port + '/');
