

- dashboard: us_map
  title: Us Map
  layout: tile
  tile_size: 100

#  filters:

  elements:  
  
  - name: add_a_unique_name_894
    title: Map of US QR Scans
    type: looker_geo_coordinates
    model: image_beanstalk
    explore: imageproccessingtable
    dimensions: [imageproccessingtable.location]
    measures: [imageproccessingtable.count]
    sorts: [imageproccessingtable.count desc 1]
    limit: 500
    show_view_names: true
    loading: false
    map: usa
    map_projection: ''
