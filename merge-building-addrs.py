#! /usr/bin/python2
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4

import sys
import os
import xml.etree.cElementTree as ElementTree
import string

outroot = ElementTree.Element("osm", { "version": "0.6" })
bldgroot = ElementTree.parse(sys.argv[1]).getroot()
addrroot = ElementTree.parse(sys.argv[2]).getroot()

waynodes = {}
bldgs = []
addrs = []

# Read the building outlines
for elem in bldgroot:
    if 'id' not in elem.attrib:
        continue
    id = int(elem.attrib['id'])
    if elem.tag == 'node':
        lat = float(elem.attrib['lat'])
        lon = float(elem.attrib['lon'])
        waynodes[id] = ( lat, lon )
        outroot.append(elem)
    if elem.tag != 'way':
        outroot.append(elem)
        continue
    tags = {
        "building": "yes"
    }
    for sub in elem:
        if sub.tag != 'tag':
            continue
        v = sub.attrib['v'].strip()
        if v:
            tags[sub.attrib['k']] = v


    # Tag transformations can happen here

    # Parse the geometry, store in a convenient format,
    # also find some point in the middle of the outline to be used to
    # speed up distance calculation
    way = []
    refs = []
    j = 0
    lat = 0.0
    lon = 0.0
    for sub in elem:
        if sub.tag != 'nd':
            continue
        ref = int(sub.attrib['ref'])
        if ref not in waynodes:
            continue
        way.append(waynodes[ref])
        refs.append(ref)
        j += 1
        lat += waynodes[ref][0]
        lon += waynodes[ref][1]
    lat /= j
    lon /= j
    if refs[0] != refs[-1]:
        outroot.append(elem)
        continue
    if 'version' in elem.attrib:
        v = int(elem.attrib['version'])
    else:
        v = 1
    bldgs.append(( lat, lon, way, refs, tags, id, v, [] ))
bldgroot = None # Make python release the XML structure

def contains(poly, pos):
    cont = 0
    prev = poly[0]
    for node in poly[1:]:
        if (node[1] > pos[1]) != (prev[1] > pos[1]) and pos[0] < node[0] + \
                (prev[0] - node[0]) * (pos[1] - node[1]) / (prev[1] - node[1]):
            cont = not cont
        prev = node
    return cont

# Read the address nodes data
for elem in addrroot:
    if 'id' not in elem.attrib:
        continue
    tags = {}
    for sub in elem:
        if sub.tag != 'tag':
            continue
        v = sub.attrib['v'].strip()
        if v:
            tags[sub.attrib['k']] = v
    if elem.tag != 'node':
        continue
    lat = float(elem.attrib['lat'])
    lon = float(elem.attrib['lon'])

    id = int(elem.attrib['id'])
    if 'version' in elem.attrib:
        v = int(elem.attrib['version'])
    else:
        v = 1
    addr = ( lat, lon, tags, id, v, [] )
    addrs.append(addr)

    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, refs, btags, id, v, newaddrs in bldgs:
        if 'addr:housenumber' in btags:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.006:
            continue
        if not contains(way, ( lat, lon )):
            continue
        newaddrs.append(addr)
        break
addrroot = None

for lat, lon, way, refs, tags, id, v, newaddrs in bldgs:
    attrs = { "version": str(v), "id": str(id) }

    # If this building contains only a single address node, copy its tags
    # to the building way and mark the node as no longer needed.
    if len(newaddrs) == 1:
        newaddrs[0][5].append(1)
        if 'source' in newaddrs[0][2]:
            newaddrs[0][2]['source:addr'] = newaddrs[0][2]['source']
            del newaddrs[0][2]['source']
        tags.update(newaddrs[0][2])
        attrs['action'] = 'modify'

    elem = ElementTree.SubElement(outroot, "way", attrs)
    for k in tags:
        ElementTree.SubElement(elem, 'tag', { 'k': k, 'v': tags[k] })
    for ref in refs:
        ElementTree.SubElement(elem, 'nd', { 'ref': str(ref) })

# Add remaining addresses as nodes
for lat, lon, tags, id, v, bbs in addrs:
    if bbs:
        continue

    i = id
    if i < 0:
        i -= 2000000
    elem = ElementTree.SubElement(outroot, "node", {
        'lat': str(lat),
        'lon': str(lon),
        "version": str(v),
        "id": str(i) })
    for k in tags:
        ElementTree.SubElement(elem, 'tag', { 'k': k, 'v': tags[k] })

sys.stdout.write("Writing .osm's\n")
ElementTree.ElementTree(outroot).write("output.osm", "utf-8")
