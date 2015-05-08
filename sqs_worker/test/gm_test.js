
var fs = require('fs')
  , gm = require('gm');
// A buffer can be passed instead of a filepath as well
var buf = fs.readFileSync('QRImage1');

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

gm(buf, 'QR1.png')
.options({imageMagick: true})
.identify("%[exif:*]", function (err, data) {
  if (err) {
  	console.log(err);
  } else {
  	console.log(data);
  	console.log(typeof data);
  	fields = data.split('\n');
  	console.log("Got field count: "+fields.length);
  	for (var f in fields) {
  		console.log(fields[f]+" is "+typeof fields[f])
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
        console.log('Missing field(s)');
    } else {
	    console.log(lat_ref+","+lat);
	    console.log(lon_ref+","+lon);
	    latitude = DegminsecToDecimal(lat_ref, lat);
	    longitude = DegminsecToDecimal(lon_ref, lon);
	    console.log("LAT: "+latitude);
	    console.log("LON: "+longitude);
	    console.log(date_time);
    }
  }
});
