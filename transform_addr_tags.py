from __future__ import print_function

import re
import xml.etree.ElementTree as ET
import expansions
import sys

# run with pypy for speed boost

INITIAL_ID = -1000

def main(infile, outfilename):
    osm = ET.parse(infile)
    root = osm.getroot()

    processed_root = newroot()

    for node in root:
        #print(node)
        house_no_node = node.find("tag[@k='HOUSE_NO']")
        address_node = node.find("tag[@k='ADDRESS']")
        if house_no_node is None:
            print("No house no. for %s" % (ET.tostring(address_node),))
            continue
        street_nam_node = node.find("tag[@k='STREET_NAM']")
        if street_nam_node is None:
            continue
        street_suffix_node = node.find("tag[@k='SUFFIX']")
        street_prefix_node = node.find("tag[@k='PREFIX']")
        zip_node = node.find("tag[@k='ZIP']")
        #import code; code.interact(local=locals())

        suffix = None
        if street_suffix_node is not None:
            if street_suffix_node.attrib['v'] in expansions.road_types:
                suffix = expansions.road_types[street_suffix_node.attrib['v']]
            else:
                suffix = street_suffix_node.attrib['v']
                print("Could not find expansion for %s" % (suffix,))

        prefix = None
        if street_prefix_node is not None:
            if street_prefix_node.attrib['v'] in expansions.directions:
                prefix = expansions.directions[street_prefix_node.attrib['v']]
            else:
                prefix = street_prefix_node.attrib['v']
                print("Could not find expansion for %s" % (prefix,))
        else:  # some roads may have directions last, like "Park Circle W"
            street_suffix_dir_node = node.find("tag[@k='SUFFIX_DIR']")
            if street_suffix_dir_node is not None:
                if street_suffix_dir_node.attrib['v'] in expansions.directions:
                    if suffix is None:
                        suffix = expansions.directions[street_suffix_dir_node.attrib['v']]
                    else:
                        suffix = "%s %s" % (suffix, expansions.directions[street_suffix_dir_node.attrib['v']])

        street = street_nam_node.attrib['v']
        if prefix:
            street = prefix + " " + street
        if suffix:
            street = street + " " + suffix


        new_tags = {
            "addr:housenumber": house_no_node.attrib['v'],
            "addr:street": street.title()
        }

        if zip_node is not None:
            new_tags['addr:postcode'] = zip_node.attrib['v']

        newnode(processed_root, node.attrib['lat'], node.attrib['lon'], new_tags)

    print("%d nodes total" % len(root))

    processed_doc = ET.ElementTree(processed_root)
    processed_doc.write(open(outfilename, 'w'), encoding="UTF-8")


def newroot():
    root = ET.Element("osm")
    root.attrib['version'] = '0.6'
    root.attrib['upload'] = 'true'
    root.attrib['generator'] = 'erjiang/cupertino-addresses'
    return root


def newnode(root, lat, lon, tags={}):
    "Creates and returns a new <node> element."
    n = ET.Element("node")
    n.attrib['id'] = newid()
    n.attrib['lat'] = lat
    n.attrib['lon'] = lon
    n.attrib['visible'] = "true"
    root.append(n)

    for k, v in tags.iteritems():
        n.append(ET.Element("tag", attrib={
            "k": k,
            "v": v
            }))

    return n


def newid():
    "Generates the next (negative) ID number."
    global INITIAL_ID
    INITIAL_ID -= 1
    return str(INITIAL_ID)


if __name__ == "__main__":

    main(sys.argv[1], sys.argv[2])
