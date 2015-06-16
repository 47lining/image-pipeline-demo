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
function writeFile(url, latitude, longitude, originalDate, bucket_name, filepath, res) {
    // filepath images/iphone_4s_pic.jpeg
    // replace file extension with "json"
    console.log(">>> writeFile: filepath: "+filepath);

    var output = {
        "key": uuid.v4(),
        "dateoriginal": originalDate,
        "url": url,
        "gpslatitude": latitude,
        "gpslongitude": longitude,
        "image": filepath
    };
    var dot = filepath.lastIndexOf(".");
    if (dot == -1) {
        jsonName = filepath+".json";
    } else {
        jsonName = filepath.substring(0, dot)+".json";
    }
    var params = {
        Bucket: bucket_name,
        Key: "metadata/"+jsonName,
        Body: JSON.stringify(output)
    };
    s3.putObject(params, function(err, data) {
      if (err) {
        console.log(err, err.stack); // an error occurred
        res.writeHead(500, 'Error writing file', {'Content-Type': 'text/plain'});
        res.end();
    } else {
        // console.log(data);
        writeDatabase(output, res);
        // res.writeHead(200, 'OK', {'Content-Type': 'text/plain'});
        // res.end();
    }
    });
}

function Frac(numerator_denominator) {
    nd = numerator_denominator.split('/');
    return nd[0]/nd[1];
}

function DegminsecToDecimal(orient, dms_str) {
    console.log("DMS in: "+dms_str);
    dms = dms_str.split(",");
    decimal = Frac(dms[0])+(Frac(dms[1])/60.0)+(Frac(dms[2])/3600.0);
    if (orient == 'S' || orient == 'W') {
        decimal = - decimal;
    }
    return decimal;
}

function processFile(bucket_name, filename, databody, res) {
    // data object has the following properties:
    // Body — (Buffer, Typed Array, Blob, String, ReadableStream) Object data.
    var image = new Image()
    image.onload = function(){
        var result;
        try {
            console.log("Starting qr decode of image...")
            var url = qrcode.decode(image).trim();
            console.log('result of qr code: ' + url);
            try {

            gm(databody, filename)
                .options({imageMagick: true})
                .identify("%[exif:*]", function (err, data) {
                    if (err) {
                        console.log(err, err.stack);
                        res.writeHead(200, 'Not Image File', {'Content-Type': 'text/plain'});
                        res.end();
                    } else {
                        fields = data.split('\n');
                        for (var f in fields) {
                            if (typeof fields[f] !== 'string') {
                                continue;
                            }
                            field = fields[f].split('=');
                            console.log("Got field: "+field[0]+", "+field[1]);
                            if (field[0]=="exif:DateTimeOriginal") {
                                date_time = field[1];
                            }
                            else if(field[0]=="exif:GPSLatitudeRef") {
                                lat_ref = field[1];
                            }
                            else if(field[0]=="exif:GPSLatitude") {
                                lat = field[1];
                            }
                            else if(field[0]=="exif:GPSLongitudeRef") {
                                lon_ref = field[1];
                            }
                            else if(field[0]=="exif:GPSLongitude") {
                                lon = field[1];
                            }
                        }
                        var bad = false;
                        if (typeof lat_ref === "undefined") {
                            console.log("Missing GPSLatitudeRef");
                            bad = true;
                        }
                        if (typeof lat === "undefined") {
                            console.log("Missing GPSLatitude");
                            bad = true;
                        }
                        if (typeof lon_ref === "undefined") {
                            console.log("Missing GPSLongitudeRef");
                            bad = true;
                        }
                        if (typeof lon === "undefined") {
                            console.log("Missing GPSLongitude");
                            bad = true;
                        }
                        if (typeof date_time === "undefined") {
                            console.log("Missing DateTimeOriginal")
                            bad = true;
                        }
                        if (bad) {
                            res.writeHead(200, 'Missing field(s)', {'Content-Type': 'text/plain'});
                            res.end();
                        } else {
                            latitude = DegminsecToDecimal(lat_ref, lat);
                            longitude = DegminsecToDecimal(lon_ref, lon);
                            writeFile(url, latitude, longitude, date_time, bucket_name, filename, res);
                        }
                    }
                }
            );
            } catch(e) {
                console.log('unable to read metadata: '+typeof e);
                res.writeHead(500, 'Unable to read metadata', {'Content-Type': 'text/plain'});
                res.end();
            }
        } catch(e) {
            console.log('unable to read qr code: '+e+', presumably not an image');
            res.writeHead(200, 'Unable to read qr code', {'Content-Type': 'text/plain'});
            res.end();
        }
    };
    console.log("Processing data byte count: "+databody.length+" from "+filename)
    image.src = databody;
}

function readFile(bucket_name, filename, res) {
    keyname = unescape(filename);
    // no idea why, but "2013-01-01 14:00:00" comes thru as "2013-01-01+14:00:00"
    keyname = keyname.replace('+', ' ');
    var params = {
        Bucket: bucket_name,
        Key: keyname
    };
    s3.getObject(params, function(err, data) {
        if (err) {
            console.log(err, err.stack); // an error occurred
            res.writeHead(500, 'OK', {'Content-Type': 'text/plain'});
            res.end();
        } else {
            // console.log(data.ContentType);
            processFile(bucket_name, filename, data.Body, res);
        }
    });
}

function handleMessage(data, res) {
    try {
        var obj = JSON.parse(data);
        console.log("Processing msg count: "+obj.Records.length)
        for (var r in obj.Records) {
            // TODO >1 record in the message?
            record = obj.Records[r];
            if (record.operation != undefined && record.operation == 'copyToRedshift') {
                console.log('Received dyn2red message: ' + body);
                rsCopy.copyToRedshift(region, dyn_tablename, body,
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
            else if (record.eventName == undefined || record.eventName.lastIndexOf("ObjectCreated:",0) != 0) {
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
                readFile(record.s3.bucket.name, record.s3.object.key, res);
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
            } else if (req.url === '/dyn2red') {
                console.log('Received dyn2red message: ' + body);
                rsCopy.copyToRedshift(region, dyn_tablename, body,
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
