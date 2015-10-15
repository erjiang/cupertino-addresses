PYTHON=pypy

output.osm: cupertino_buildings_untagged.osm cupertino_addresses_tagged.osm
	time $(PYTHON) dfa9d7ac5e784ce8b94f/merge-building-addrs.py cupertino_buildings_untagged.osm cupertino_addresses_tagged.osm

cupertino_buildings_untagged.osm: cupertino_buildings.osm
	grep -v tag $< > $@

cupertino_addresses_tagged.osm: cupertino_addresses.osm
	time $(PYTHON) transform_addr_tags.py $< $@
