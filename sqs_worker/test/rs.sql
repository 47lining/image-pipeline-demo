COPY imageprocessingtable from 
	'dynamodb://table-impagep3'
    credentials 'aws_access_key_id=AKIAI4MPNWVZMQY2YBRA;aws_secret_access_key=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'
    READRATIO 100
    TIMEFORMAT AS 'YYYY-MM-DD HH:MI:SS' 



DROP TABLE IF EXISTS imageprocessingtable CASCADE;
CREATE TABLE imageprocessingtable
(
  key          varchar(50)     NOT NULL,
  url          varchar(200)    NOT NULL,
  dateoriginal  timestamp      NOT NULL,
  gpslatitude  float8          NOT NULL,
  gpslongitude  float8          NOT NULL,
  image        varchar(100)
);

COMMIT;

delete from imageprocessingtable;