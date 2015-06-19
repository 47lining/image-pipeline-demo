var 
    fs = require('fs'),
    AWS = require('aws-sdk'),
    uuid=require('uuid'),
    gm = require('gm'),
    Canvas = require('canvas'),
    Image = Canvas.Image,
    qrcode = require('jsqrcode')(Canvas),
    s3 = new AWS.S3(),
	imageProc = new Object();

function writeFile(url, latitude, longitude, originalDate, bucket_name, filepath, callback) {
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
            callback(err, 'Error writing file');
	    } else {
            callback(undefined, output);
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

function processFile(bucket_name, filename, databody, callback) {
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
                        callback(undefined, 'Not Image File')
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
                            writeFile(url, latitude, longitude, date_time, bucket_name, filename, callback);
                        }
                    }
                }
            );
            } catch(e) {
                console.log('unable to read metadata: '+typeof e);
                callback(e, 'unable to read metadata');
            }
        } catch(e) {
            console.log('unable to read qr code: '+e+', presumably not an image');
            callback(undefined, 'Unable to read qr code, not an image');
        }
    };
    console.log("Processing data byte count: "+databody.length+" from "+filename)
    image.src = databody;
}

// 
// callback function:  err, data.
// if real error, err will be returned
// otherwise err undefined.
// if data processed, data will be a dict, else string
imageProc.readFile = function(bucket_name, filename, callback) {
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
        	callback(err);
        } else {
            // console.log(data.ContentType);
            processFile(bucket_name, filename, data.Body, callback);
        }
    });
}

module.exports=imageProc;
