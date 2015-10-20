#! /usr/bin/python2
# vim: fileencoding=utf-8 et sw=4

from collections import namedtuple
import sys
import os
import xml.etree.cElementTree as ElementTree
import string


Building = namedtuple('Building', 'lat lon way refs tags id v newaddrs')
Relation = namedtuple('Relation', 'id members tags newaddrs')
# bound is bool that indicates whether Addr was merged into building
# and thus should not be added as node
Addr = namedtuple('Addr', 'lat lon tags id v bound')


outroot = ElementTree.Element("osm", { "version": "0.6" })
bldgroot = ElementTree.parse(sys.argv[1]).getroot()
addrroot = ElementTree.parse(sys.argv[2]).getroot()

# map way ID to relation ID
# assumes each way is member of at most 1 relation
relation_membership = {}

waynodes = {}
bldgs = []
# map relation IDs to Relation objects
rltns = {}
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
        continue

    if elem.tag == 'relation':
        members = []
        for member in elem:
            if member.tag == 'member':
                # record that this way belongs to this relation
                relation_membership[member.attrib['ref']] = elem.attrib['id']
                members.append(member)

    # Tag transformations happen here
    orig_tags = {}
    tags = {
        "building": "yes"
    }
    for sub in elem:
        if sub.tag != 'tag':
            continue
        v = sub.attrib['v'].strip()
        if v:
            orig_tags[sub.attrib['k']] = v
    if 'Height' in orig_tags:
        # need to convert units from ft to m
        # but there seems to only be ft precision
        tags['height'] = "%.1f" % (float(orig_tags['Height']) / 3.281,)
    # copy "type" tag for relations
    if 'type' in orig_tags:
        tags['type'] = orig_tags['type']

    # Parse the geometry, store in a convenient format,
    # also find some point in the middle of the outline to be used to
    # speed up distance calculation
    if elem.tag == 'way':
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
        bldgs.append(Building(lat, lon, way, refs, tags, id, v, []))
    elif elem.tag == 'relation':
        rltns[elem.attrib['id']] = Relation(elem.attrib['id'], members, tags, [])
        
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
    addr = Addr(lat, lon, tags, id, v, [])
    addrs.append(addr)

    # Find what if any building shapes contain this lat/lon
    #for elat, elon, way, refs, btags, id, v, newaddrs in bldgs:
    for bldg in bldgs:
        if 'addr:housenumber' in bldg.tags:
            continue
        if abs(bldg.lat - lat) + abs(bldg.lon - lon) > 0.006:
            continue
        if not contains(bldg.way, ( lat, lon )):
            continue
        # if this way is part of a relation, resolve to relation
        if bldg.id in relation_membership:
            rel_id = relation_membership[bldg.id]
            rltns[rel_id].newaddrs.append(addr)
        else:
            bldg.newaddrs.append(addr)
        break
addrroot = None

#for lat, lon, way, refs, tags, id, v, newaddrs in bldgs:
for bldg in bldgs:
    attrs = { "version": str(bldg.v), "id": str(bldg.id) }

    # If this building contains only a single address node, copy its tags
    # to the building way and mark the node as no longer needed.
    if len(bldg.newaddrs) == 1:
        bldg.newaddrs[0].bound.append(True)
        tags.update(bldg.newaddrs[0].tags)
        attrs['action'] = 'modify'

    elem = ElementTree.SubElement(outroot, "way", attrs)
    for k in bldg.tags:
        ElementTree.SubElement(elem, 'tag', { 'k': k, 'v': bldg.tags[k] })
    for ref in bldg.refs:
        ElementTree.SubElement(elem, 'nd', { 'ref': str(ref) })

# Add remaining addresses as nodes
#for lat, lon, tags, id, v, bbs in addrs:
for addr in addrs:
    if addr.bound:
        continue

    i = id
    if i < 0:
        i -= 2000000
    elem = ElementTree.SubElement(outroot, "node", {
        'lat': str(addr.lat),
        'lon': str(addr.lon),
        "version": str(addr.v),
        "id": str(i) })
    for k in addr.tags:
        ElementTree.SubElement(elem, 'tag', { 'k': k, 'v': addr.tags[k] })

sys.stdout.write("Writing .osm's\n")
ElementTree.ElementTree(outroot).write("output.osm", "utf-8")
