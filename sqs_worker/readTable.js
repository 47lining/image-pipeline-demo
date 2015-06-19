var 
  vogels = require('vogels'),
  Joi = require('joi'),
  tableScanner = new Object(),
  Metadata_schema = {
    hashKey : 'key',

    // add the timestamp attributes (updatedAt, createdAt)
    timestamps : false,

    schema : {
      key          : Joi.string(),
      dateoriginal : Joi.string(),
      image        : Joi.string(),
      url          : Joi.string(),
      gpslatitude  : Joi.number(),
      gpslongitude : Joi.number(),
    }
  };

// Returns data.Items[] and data.Count
tableScanner.scanMetadata = function(tablename, callback) {
  Metadata_schema['tableName'] = tablename;
  var Metadata = vogels.define('Metadata', Metadata_schema);
  Metadata
    .scan()
    .loadAll()
    .exec(callback);
};

module.exports = tableScanner;
