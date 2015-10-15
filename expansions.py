"""
Data from observation and Appendix B (p271) of 
http://www.census.gov/geo/www/tiger/tiger2006se/TGR06SE.pdf
"""
# tiger:name_type
road_types = {
    'ALY': 'Alley',
    'ARC': 'Arcade',
    'AVE': 'Avenue',
    'BLF': 'Bluff',
    'BLVD': 'Boulevard',
    'BR': 'Bridge',
    'BRG': 'Bridge',
    'BYP': 'Bypass',
    'CIR': 'Circle',
    'CMN': 'Common',
    'CRES': 'Crescent',
    'CSWY': 'Causeway',
    'CT': 'Court',
    'CTR': 'Center',
    'CV': 'Cove',
    'DR': 'Drive',
    'EXPY': 'Expressway',
    'EXPWY': 'Expressway',
    'FMRD': 'Farm to Market Road',
    'FWY': 'Freeway',
    'GRD': 'Grade',
    'HBR': 'Harbor',
    'HOLW': 'Hollow',
    'HWY': 'Highway',
    'LN': 'Lane',
    'LNDG': 'Landing',
    'MAL': 'Mall',
    'MTWY': 'Motorway',
    'OVPS': 'Overpass',
    'PKY': 'Parkway',
    'PKWY': 'Parkway',
    'PL': 'Place',
    'PLZ': 'Plaza',
    'RD': 'Road',
    'RDG': 'Ridge',
    'RMRD': 'Ranch to Market Road',
    'RTE': 'Route',
    'SKWY': 'Skyway',
    'SQ': 'Square',
    'ST': 'Street',
    'TER': 'Terrace',
    'TFWY': 'Trafficway',
    'THFR': 'Thoroughfare',
    'THWY': 'Thruway',
    'TPKE': 'Turnpike',
    'TRCE': 'Trace',
    'TRL' : 'Trail',
    'TUNL': 'Tunnel',
    'UNP': 'Underpass',
    'WKWY': 'Walkway',
    'XING': 'Crossing',
    ### NOT EXPANDED
    'WAY': 'Way',
    'WALK': 'Walk',
    'LOOP': 'Loop',
    'OVAL': 'Oval',
    'RAMP': 'Ramp',
    'ROW': 'Row',
    'RUN': 'Run',
    'PASS': 'Pass',
    'SPUR': 'Spur',
    'PATH': 'Path',
    'PIKE': 'Pike',
    'RUE': 'Rue',
    'MALL': 'Mall',
    }

# tiger:name_direction_prefix/tiger:name_direction_suffix
directions = {
    'N': 'North',
    'S': 'South',
    'E': 'East',
    'W': 'West',
    'NE': 'Northeast',
    'NW': 'Northwest',
    'SE': 'Southeast',
    'SW': 'Southwest'}
