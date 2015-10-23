from __future__ import division, print_function

from collections import namedtuple, defaultdict
import sys
import os
import xml.etree.ElementTree as ET


"""This script naively separates a data file into regions based on a file of
shapes. Since it does simple BBox center testing, it's no good for data that
crosses boundaries."""


def main(region_file, data_file, out_dir):

    region_root = ET.parse(region_file).getroot()
    print("Loaded regions XML")

    # map region ID to objects
    region_data = process_regions(region_root)
    print("Processed regions")

    data_root = ET.parse(data_file).getroot()
    print("Loaded data XML")

    regions = sort_buildings(region_data, data_root)
    print("Sorted data into regions")

    write_regions(regions, out_dir)
    print("Wrote XML files")


def process_regions(region_root):
    # map node ID to (lat, lon)
    region_nodes = {}
    # map region ID to objects
    region_data = {}

    # collect all nodes
    for elem in region_root:
        if elem.tag == 'node':
            region_nodes[elem.attrib['id']] = (float(elem.attrib['lat']), float(elem.attrib['lon']))
    # collect all ways
    for elem in region_root:
        if elem.tag == 'way':
            region_id = elem.attrib['id']
            coords = []
            for n in elem:
                coords.append(region_nodes[n.attrib['ref']])
            region_data[region_id] = coords
    return region_data


def sort_buildings(region_data, data_root):
    # map regions to list of ET elements
    regions = defaultdict(list)

    # map node ID to region ID
    item_membership = dict()

    for elem in data_root:
        if elem.tag == 'node':
            lat = float(elem.attrib['lat'])
            lon = float(elem.attrib['lon'])
            r_id = which_region(region_data, (lat, lon))
            regions[r_id].append(elem)
            #print("Adding node %s to region %s" % (elem.attrib['id'], r_id))
            item_membership[elem.attrib['id']] = r_id
    for elem in data_root:
        if elem.tag == 'way':
            for child in elem:
                if child.tag == 'nd':
                    r_id = item_membership[child.attrib['ref']]
                    regions[r_id].append(elem)
                    #print("Adding way %s to region %s" % (elem.attrib['id'], r_id))
                    item_membership[elem.attrib['id']] = r_id
                    break
    for elem in data_root:
        if elem.tag == 'relation':
            for child in elem:
                if child.tag == 'member':
                    r_id = item_membership[child.attrib['ref']]
                    regions[r_id].append(elem)
                    #print("Adding relation %s to region %s" % (elem.attrib['id'], r_id))
                    item_membership[elem.attrib['id']] = r_id
                    break 
    return regions

def which_region(region_data, point):
    for r_id, r_coords in region_data.items():
        if contains(r_coords, point):
            return r_id
    return None


def bb_center(poly):
    """Given [(x, y), ...], return the center of the bbox as (x, y)."""
    min_x = max_x = poly[0][0]
    min_y = max_y = poly[0][1]
    for x, y in poly:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    return ((max_x + min_x) / 2, (max_y + min_y) / 2)


def contains(poly, pos):
    """Copied from merge-building-addrs. poly is a list of lat/lon coords. pos
    is (lat, lon) tuple."""
    cont = 0
    prev = poly[0]
    for node in poly[1:]:
        if (node[1] > pos[1]) != (prev[1] > pos[1]) and pos[0] < node[0] + \
                (prev[0] - node[0]) * (pos[1] - node[1]) / (prev[1] - node[1]):
            cont = not cont
        prev = node
    return cont


def write_regions(regions, out_dir):
    for r_id, elems in regions.items():
        outroot = ET.Element("osm", {
            "version": "0.6",
            "generator": "chunks.py"
        })

        outroot.extend(elems)

        ET.ElementTree(outroot).write("%s/%s.osm" % (out_dir, r_id), "utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
