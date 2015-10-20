# cupertino-addresses
Proposed import of cupertino buildings and addresses for OSM

# Contents

Included in this repo are data provided by the city of Cupertino. The data has its original tags - mainly it was converted from shapefiles to OSM XML.

# Usage

If you have pypy, you can just run `make` and all the data will be processed. If you don't have pypy, you can change the `PYTHON` variable in the Makefile to point to your Python version. If you are using CPython, you can also change `xml.etree.ElementTree` to `xml.etree.cElementTree` for faster processing.

The file `output.osm` is the import-ready OSM data.
