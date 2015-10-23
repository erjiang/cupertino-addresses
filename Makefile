PYTHON=pypy

regions: output.osm cupertino_regions.osm
	mkdir -p $@
	time $(PYTHON) chunks.py cupertino_regions.osm output.osm $@

output.osm: cupertino_buildings.osm cupertino_addresses_tagged.osm
	time $(PYTHON) ./merge-building-addrs.py cupertino_buildings.osm cupertino_addresses_tagged.osm

cupertino_addresses_tagged.osm: cupertino_addresses.osm
	time $(PYTHON) transform_addr_tags.py $< $@
