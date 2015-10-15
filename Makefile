PYTHON=pypy

cupertino_addresses_tagged.osm: cupertino_addresses.osm
	time $(PYTHON) transform_addr_tags.py $< $@
