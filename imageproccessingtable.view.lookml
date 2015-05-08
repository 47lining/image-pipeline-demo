- view: imageproccessingtable
  sql_table_name: public.imageproccessingtable
  fields:

  - dimension_group: dateoriginal
    type: time
    timeframes: [time, date, week, month]
    sql: ${TABLE}.dateoriginal

  - dimension: location
    type: location
    sql_latitude: ${TABLE}.gpslatitude
    sql_longitude: ${TABLE}.gpslongitude

  - dimension: image
    sql: ${TABLE}.image

  - dimension: url
    sql: ${TABLE}.url

  - measure: count
    type: count
    drill_fields: []
